#!/usr/bin/env python3
"""Offline structural validation for environments without DevOps CLIs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "Dockerfile",
    "app/server.py",
    "app/tests/test_server.py",
    "infrastructure/terraform/main.tf",
    "infrastructure/terraform/modules/network/main.tf",
    "infrastructure/terraform/modules/eks/main.tf",
    "platform/chart/Chart.yaml",
    "platform/chart/values.yaml",
    "gitops/applications/cloudforge.yaml.tpl",
    "policies/require-secure-workloads.yaml",
    "observability/cloudforge-dashboard.json",
    ".github/workflows/ci.yml",
    ".github/workflows/deploy-demo.yml",
    ".github/workflows/destroy-demo.yml",
]

YAML_FILES = [
    "compose.yaml",
    "platform/chart/Chart.yaml",
    "platform/chart/values.yaml",
    "observability/kube-prometheus-values.yaml",
    "policies/require-secure-workloads.yaml",
    "gitops/applications/cloudforge.yaml.tpl",
    ".github/workflows/ci.yml",
    ".github/workflows/deploy-demo.yml",
    ".github/workflows/destroy-demo.yml",
]

SECRET_PATTERNS = {
    "AWS access key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{30,}"),
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


class CloudFormationLoader(yaml.SafeLoader):
    pass


def cloudformation_tag(loader: CloudFormationLoader, tag_suffix: str, node: yaml.Node) -> object:
    if isinstance(node, yaml.ScalarNode):
        return {tag_suffix: loader.construct_scalar(node)}
    if isinstance(node, yaml.SequenceNode):
        return {tag_suffix: loader.construct_sequence(node)}
    return {tag_suffix: loader.construct_mapping(node)}


CloudFormationLoader.add_multi_constructor("!", cloudformation_tag)


def validate_hcl_balance(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    without_comments = re.sub(r"(?m)#.*$|//.*$", "", text)
    without_strings = re.sub(r'"(?:\\.|[^"\\])*"', '""', without_comments)
    for opening, closing in [("{", "}"), ("[", "]"), ("(", ")")]:
        if without_strings.count(opening) != without_strings.count(closing):
            fail(f"unbalanced {opening}{closing} delimiters in {path.relative_to(ROOT)}")


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail(f"required files are missing: {', '.join(missing)}")

    for relative in YAML_FILES:
        path = ROOT / relative
        try:
            list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
        except yaml.YAMLError as exc:
            fail(f"invalid YAML in {relative}: {exc}")

    bootstrap = yaml.load(
        (ROOT / "bootstrap/aws-oidc-role.yaml").read_text(encoding="utf-8"),
        Loader=CloudFormationLoader,
    )
    if not {"GitHubOIDCProvider", "TerraformStateBucket", "GitHubDeployRole"}.issubset(bootstrap["Resources"]):
        fail("CloudFormation bootstrap is missing required resources")

    for terraform_file in (ROOT / "infrastructure/terraform").rglob("*.tf"):
        validate_hcl_balance(terraform_file)

    dashboard = json.loads((ROOT / "observability/cloudforge-dashboard.json").read_text())
    if not dashboard.get("panels") or dashboard.get("uid") != "cloudforge-overview":
        fail("Grafana dashboard is missing its UID or panels")

    combined = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in ROOT.rglob("*")
        if path.is_file() and ".git" not in path.parts
    )
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(combined):
            fail(f"possible {name} detected")

    dockerfile = (ROOT / "Dockerfile").read_text()
    for control in ["USER 65532:65532", "HEALTHCHECK", "ENTRYPOINT"]:
        if control not in dockerfile:
            fail(f"Dockerfile is missing required control: {control}")

    deployment = (ROOT / "platform/chart/templates/deployment.yaml").read_text()
    for control in ["runAsNonRoot: true", "readOnlyRootFilesystem: true", "allowPrivilegeEscalation: false"]:
        if control not in deployment:
            fail(f"Kubernetes deployment is missing required control: {control}")

    print(
        f"Validated {len(REQUIRED_FILES)} required files, {len(YAML_FILES)} YAML files, "
        "CloudFormation structure, Terraform delimiter balance, dashboard JSON, secret patterns, "
        "and workload security controls."
    )


if __name__ == "__main__":
    main()
