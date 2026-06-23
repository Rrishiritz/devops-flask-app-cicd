FROM jenkins/jenkins:lts

USER root
RUN apt-get update && \
  apt-get install -y curl bash && \
  apt-get install -y docker.io bash && \
  groupadd -f docker && \
  usermod -aG docker jenkins && \
  curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64 && \
  chmod +x /usr/local/bin/argocd

#USER jenkins
