pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO  = "rishi1raj/flask-ml-backend"
    IMAGE_TAG        = "${env.BUILD_ID}"
    ARGOCD_SERVER    = "host.docker.internal:30443"
    ARGOCD_CREDS     = credentials('argocd-creds')
    ARGOCD_APP       = "flask-app"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
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
          set -euo pipefail
          echo "$DOCKER_HUB_CREDS_PSW" | docker login -u "$DOCKER_HUB_CREDS_USR" --password-stdin
          docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
        '''
      }
    }

    stage('Sync Argo CD') {
      steps {
        sh '''
          set -euo pipefail
          ARGO_HOST=${ARGOCD_SERVER}

          # wait for Argo CD health
          for i in $(seq 1 20); do
            if curl -k --connect-timeout 10 https://${ARGO_HOST}/healthz >/dev/null 2>&1; then
              echo "Argo CD reachable"
              break
            fi
            echo "waiting for Argo CD... ($i/20)"
            sleep 5
          done

          # login with retries using grpc-web
          for i in $(seq 1 8); do
            echo "argocd login attempt $i"
            if argocd login ${ARGO_HOST} --grpc-web --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug; then
              echo "argocd login succeeded"
              break
            fi
            echo "login failed, retrying..."
            sleep 5
          done

          # sync app explicitly with server and grpc-web
          argocd app sync ${ARGOCD_APP} --server ${ARGO_HOST} --grpc-web --insecure
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
