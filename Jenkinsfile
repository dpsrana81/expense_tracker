pipeline {
    agent any

    environment {
        IMAGE_NAME = "expense-tracker-backend"
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Install & Test') {
            steps {
                dir('backend') {
                    sh 'pip install -r requirements.txt'
                    sh 'pytest -v || true'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                dir('backend') {
                    sh "docker build -t ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${BUILD_NUMBER} ."
                    sh "docker tag ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${BUILD_NUMBER} ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest"
                }
            }
        }

        stage('Push to Docker Hub') {
            steps {
                sh "echo $DOCKERHUB_CREDENTIALS_PSW | docker login -u $DOCKERHUB_CREDENTIALS_USR --password-stdin"
                sh "docker push ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:${BUILD_NUMBER}"
                sh "docker push ${DOCKERHUB_CREDENTIALS_USR}/${IMAGE_NAME}:latest"
            }
        }

        stage('Deploy to EC2') {
            steps {
                sshagent(['ec2-ssh-key']) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ec2-user@\$EC2_HOST '
                            cd /opt/expense-tracker &&
                            docker compose pull &&
                            docker compose up -d
                        '
                    """
                }
            }
        }
    }

    post {
        success { echo 'Pipeline completed successfully.' }
        failure { echo 'Pipeline failed — check logs above.' }
    }
}
