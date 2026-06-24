pipeline {
  agent any

  environment {
    DOCKER_HUB_CREDS = credentials('docker-hub-creds')
    DOCKER_HUB_REPO  = "rishi1raj/flask-ml-backend"
    IMAGE_TAG        = "${env.BUILD_ID}"
    GIT_CREDS        = credentials('github-creds')   // Jenkins credential with GitHub username/password or token
    GIT_REPO         = "https://github.com/Rrishiritz/devops-flask-app-cicd.git"
    VALUES_FILE      = "k8s/flask-app/values.dockerhub.yaml"
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

    stage('Update GitHub values file') {
      steps {
        sh '''
          set -euo pipefail
          # update the image tag in values.dockerhub.yaml
          sed -i "s|tag:.*|tag: ${IMAGE_TAG}|g" ${VALUES_FILE}

          git config --global user.email "jenkins@ci.local"
          git config --global user.name "Jenkins CI"

          git add ${VALUES_FILE}
          git commit -m "Update image tag to ${IMAGE_TAG}"
          git push https://${GIT_CREDS_USR}:${GIT_CREDS_PSW}@github.com/Rrishiritz/devops-flask-app-cicd.git HEAD:main
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
