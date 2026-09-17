# CloudForge Demonstration Script

Record a three- to five-minute screen capture after the AWS deployment workflow succeeds.

## Preparation

```bash
aws eks update-kubeconfig --name cloudforge-demo --region us-east-2
kubectl get nodes
kubectl get applications -n argocd
kubectl get pods,service,hpa -n cloudforge
```

Start the service locally through Kubernetes:

```bash
kubectl port-forward service/cloudforge 8080:80 -n cloudforge
```

In a second terminal, show the API and metrics:

```bash
curl http://127.0.0.1:8080/
curl http://127.0.0.1:8080/healthz
curl http://127.0.0.1:8080/metrics
```

## Recording sequence

1. Open the repository and explain the architecture diagram.
2. Show the successful CI workflow and its test, Terraform, Helm and security jobs.
3. Show the EKS nodes, application replicas and Argo CD application health.
4. Show Grafana through `kubectl port-forward service/monitoring-grafana 3000:80 -n monitoring`.
5. Generate traffic with `python scripts/load-test.py` and show the request-rate dashboard.
6. Demonstrate self-healing by deleting one application pod and watching Kubernetes replace it.
7. Demonstrate GitOps drift correction by temporarily changing the pod termination grace period and showing Argo CD restore the declared value:

   ```bash
   kubectl patch deployment cloudforge -n cloudforge --type merge \
     -p '{"spec":{"template":{"spec":{"terminationGracePeriodSeconds":7}}}}'
   kubectl get deployment cloudforge -n cloudforge \
     -o jsonpath='{.spec.template.spec.terminationGracePeriodSeconds}'
   ```

   Within the next synchronization cycle, the value should return to `15`.
8. End with the successful destroy workflow and the AWS resource cleanup evidence.

Never show account IDs, browser credentials, tokens, kubeconfig contents, or secret values in the recording.
