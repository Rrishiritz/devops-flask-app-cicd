pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO = "rishi1raj/flask-ml-backend"
    IMAGE_TAG = "${env.BUILD_ID}"
    ARGOCD_SERVER = "argocd-server.argocd.svc.cluster.local:443"
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
          argocd login ${ARGOCD_SERVER} --username ${ARGOCD_CREDS_USR} --password ${ARGOCD_CREDS_PSW} --insecure
          argocd app sync ${ARGOCD_APP}
        '''
      }
    }
  }

  post {
    always {
      sh 'docker logout'
    }
  }
}
