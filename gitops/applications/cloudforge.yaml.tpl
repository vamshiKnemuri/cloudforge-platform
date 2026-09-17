apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloudforge
  namespace: argocd
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: ${GITOPS_REPO_URL}
    targetRevision: main
    path: platform/chart
    helm:
      parameters:
        - name: image.repository
          value: ${IMAGE_REPOSITORY}
        - name: image.tag
          value: ${IMAGE_TAG}
        - name: environment
          value: demo
  destination:
    server: https://kubernetes.default.svc
    namespace: cloudforge
  syncPolicy:
    automated:
      enabled: true
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m

