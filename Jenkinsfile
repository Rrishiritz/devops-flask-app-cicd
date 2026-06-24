pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO = "rishi1raj/flask-ml-backend"
    IMAGE_TAG = "${env.BUILD_ID}"
    ARGOCD_LOCAL = "127.0.0.1:8084"
    ARGOCD_CREDS = credentials('argocd-creds')
    ARGOCD_APP = "flask-app"
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
          # start port-forward inside the agent
          kubectl -n argocd port-forward svc/argocd-server 8084:443 >/tmp/argocd-pf.log 2>&1 &
          PF_PID=$!

          # wait for local port to be ready
          for i in {1..12}; do
            nc -vz 127.0.0.1 8084 >/dev/null 2>&1 && break
            echo "waiting for local port-forward..."
            sleep 2
          done

          curl -k --connect-timeout 5 https://127.0.0.1:8084/healthz

          # login (try gRPC then grpc-web)
          if argocd login ${ARGOCD_LOCAL} --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug; then
            echo "argocd login succeeded"
          else
            argocd login ${ARGOCD_LOCAL} --grpc-web --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug
          fi

          argocd app sync ${ARGOCD_APP}

          # cleanup
          kill $PF_PID || true
          rm -f /tmp/argocd-pf.log || true
        '''
      }
    }
  }

  post {
    always { sh 'docker logout || true' }
  }
}
