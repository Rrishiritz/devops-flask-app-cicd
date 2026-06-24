pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO = "rishi1raj/flask-ml-backend"
    IMAGE_TAG = "${env.BUILD_ID}"
    ARGOCD_CREDS = credentials('argocd-creds')
    ARGOCD_APP = "flask-app"
    ARGOCD_LOCAL = "127.0.0.1:8084"
    KUBECONFIG = "/home/jenkins/.kube/config"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Build Docker image') {
      steps {
        dir('flask-app') {
          sh 'docker build -t ${DOCKER_HUB_REPO}:${IMAGE_TAG} .'
        }
      }
    }

    stage('Push Docker image') {
      steps {
        sh '''
          echo "$DOCKER_HUB_CREDS_PSW" | docker login -u "$DOCKER_HUB_CREDS_USR" --password-stdin
          docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
        '''
      }
    }

    stage('Port-forward and Sync ArgoCD') {
      steps {
        sh '''
          set -euo pipefail

          command -v kubectl >/dev/null 2>&1 || { echo "kubectl not found"; exit 1; }
          command -v argocd >/dev/null 2>&1 || { echo "argocd not found"; exit 1; }

          export KUBECONFIG=${KUBECONFIG}

          kubectl -n argocd port-forward svc/argocd-server 8084:443 >/tmp/argocd-pf.log 2>&1 &
          PF_PID=$!
          echo "started port-forward pid=$PF_PID"

          for i in $(seq 1 12); do
            if nc -vz 127.0.0.1 8084 >/dev/null 2>&1; then
              echo "local port 127.0.0.1:8084 is open"
              break
            fi
            echo "waiting for local port-forward... ($i/12)"
            sleep 2
          done

          if ! nc -vz 127.0.0.1 8084 >/dev/null 2>&1; then
            echo "port-forward did not bind; last 200 lines of log:"
            tail -n 200 /tmp/argocd-pf.log || true
            kill $PF_PID 2>/dev/null || true
            exit 1
          fi

          curl -k --connect-timeout 5 https://127.0.0.1:8084/healthz

          if argocd login ${ARGOCD_LOCAL} --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug; then
            echo "argocd login (gRPC) succeeded"
          else
            echo "gRPC login failed; trying grpc-web"
            argocd login ${ARGOCD_LOCAL} --grpc-web --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug
          fi

          argocd app sync ${ARGOCD_APP}

          kill $PF_PID || true
          rm -f /tmp/argocd-pf.log || true
        '''
      }
    }
  }

  post {
    always {
      sh 'docker logout || true'
    }
  }
}
