FROM jenkins/jenkins:lts

# Use root to install extra tools if needed, then switch back to jenkins user.
USER root

# Example: install git if needed
# RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

USER jenkins

# Default Jenkins home is /var/jenkins_home and will be persisted by Docker Compose.
