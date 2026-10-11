# AI Analytics Dashboard — Jenkins and Minikube

This branch adds Jenkins CI/CD and Kubernetes manifests. The original GitHub Actions/Ansible workflow is retained; avoid running both deployment paths simultaneously against the same app.

## EC2 prerequisites
Install Docker, Python 3, Jenkins, kubectl and Minikube. Start a Docker-driver Minikube cluster under ubuntu. Grant Jenkins access to the Docker group and a working Minikube/kubeconfig profile. Test both as the jenkins user before running the pipeline.

## Create secret (never commit API keys)
```bash
read -rsp "OpenRouter API key: " OPENROUTER_API_KEY; echo
kubectl create secret generic analytics-secrets --from-literal=OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
unset OPENROUTER_API_KEY
```

## Jenkins job
Create a Pipeline job using Pipeline script from SCM, Git URL https://github.com/Sakshi123u/AI-Driven-Analytics-Dashboard-Devops.git, branch */feature/jenkins-minikube-deployment, Script Path Jenkinsfile. Click Build Now after prerequisites are ready.

## Check
```bash
kubectl get deployments,pods,services
kubectl rollout status deployment/analytics-dashboard
kubectl port-forward --address 127.0.0.1 service/analytics-dashboard 8503:8501
```
In another EC2 terminal: curl -I http://localhost:8503/_stcore/health

To expose externally, use an authenticated reverse proxy or SSH tunnel; do not expose cluster management ports.
