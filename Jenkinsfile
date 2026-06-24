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
          echo "$DOCKER_HUB_CREDS_PSW" | docker login -u "$DOCKER_HUB_CREDS_USR" --password-stdin
          docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
        '''
      }
    }

stage('Sync Argo CD') {
    steps {
        sh '''
        # Wait for Argo CD to be reachable
        for i in {1..10}; do
            if curl -k --connect-timeout 10 https://host.docker.internal:30443 >/dev/null 2>&1; then
                echo "Argo CD is reachable"
                break
            else
                echo "Argo CD not reachable, retrying in 5 seconds..."
                sleep 5
            fi
        done

        # Login with retry
        for i in {1..5}; do
            argocd login ${ARGOCD_SERVER} --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure && break
            echo "Login failed, retrying in 5 seconds..."
            sleep 5
        done

        # Sync app
        argocd app sync ${ARGOCD_APP}
        '''
    }
}
    }
  }

  post {
    always {
      sh 'docker logout'
    }
  }
}
