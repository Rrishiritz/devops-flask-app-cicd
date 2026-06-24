pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO = "rishi1raj/flask-ml-backend"
    IMAGE_TAG = "${env.BUILD_ID}"
    ARGOCD_SERVER = "host.docker.internal:30443"
    ARGOCD_CREDS = credentials('argocd-creds')
    ARGOCD_APP = "flask-app"
  }

  stages {
    stage('Checkout') { steps { checkout scm } }

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

    stage('Sync Argo CD') {
      steps {
        sh '''
          for i in {1..20}; do
            curl -k --connect-timeout 10 https://${ARGOCD_SERVER}/healthz >/dev/null 2>&1 && break
            echo "waiting for argocd..."
            sleep 5
          done

          if argocd login ${ARGOCD_SERVER} --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug; then
            echo "gRPC login succeeded"
          else
            echo "gRPC failed; trying grpc-web"
            argocd login ${ARGOCD_SERVER} --grpc-web --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure --loglevel debug
          fi

          argocd app sync ${ARGOCD_APP}
        '''
      }
    }
  }

  post {
    always { sh 'docker logout || true' }
  }
}
