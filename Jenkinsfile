pipeline {
  agent any

  environment {
    DOCKER_HUB_USERNAME = credentials('docker-hub-username')
    DOCKER_HUB_PASSWORD = credentials('docker-hub-password')
    DOCKER_HUB_REPO = "your-dockerhub-username/rishiapp"
    IMAGE_TAG = "${env.BUILD_ID}"
    ARGOCD_SERVER = "argocd-server.argocd.svc.cluster.local:443"
    ARGOCD_USERNAME = "admin"
    ARGOCD_PASSWORD = credentials('argocd-password')
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
          echo "$DOCKER_HUB_PASSWORD" | docker login -u "$DOCKER_HUB_USERNAME" --password-stdin
          docker push ${DOCKER_HUB_REPO}:${IMAGE_TAG}
        '''
      }
    }

    stage('Sync Argo CD') {
      steps {
        sh '''
          argocd login ${ARGOCD_SERVER} --username ${ARGOCD_USERNAME} --password ${ARGOCD_PASSWORD} --insecure
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
