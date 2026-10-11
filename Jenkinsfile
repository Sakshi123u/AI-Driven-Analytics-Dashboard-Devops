pipeline {
  agent any
  options { timestamps() }
  environment {
    IMAGE_NAME = 'analytics-dashboard'
    IMAGE_TAG = "${BUILD_NUMBER}"
  }
  stages {
    stage('Checkout') { steps { checkout scm } }
    stage('Python Syntax') { steps { sh 'python3 -m compileall -q app' } }
    stage('Build Docker Image') { steps { sh 'docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ./app' } }
    stage('Load into Minikube') { steps { sh 'minikube image load ${IMAGE_NAME}:${IMAGE_TAG}' } }
    stage('Deploy') { steps { sh '''
      kubectl apply -f k8s/service.yaml
      kubectl apply -f k8s/deployment.yaml
      kubectl set image deployment/analytics-dashboard analytics-dashboard=${IMAGE_NAME}:${IMAGE_TAG}
    ''' } }
    stage('Verify') { steps { sh '''
      kubectl rollout status deployment/analytics-dashboard --timeout=240s
      kubectl get pods -l app=analytics-dashboard
      kubectl get service analytics-dashboard
    ''' } }
  }
}