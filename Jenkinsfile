pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
        timestamps()
        timeout(time: 20, unit: 'MINUTES')
    }
    triggers { pollSCM('H/2 * * * *') }
    environment {
        TEST_IMAGE = "aceest-test:${BUILD_NUMBER}"
        RUNTIME_IMAGE = "aceest-runtime:${BUILD_NUMBER}"
        TEST_CONTAINER = "aceest-tests-${BUILD_NUMBER}"
        DOCKER_REPO = "2025tm93113/aceest-fitness"
    }
    stages {
        stage('Clean checkout') {
            steps { deleteDir(); checkout scm }
        }
        stage('Clean Docker build') {
            steps {
                sh 'docker version'
                sh 'docker build --pull --no-cache --target test -t "$TEST_IMAGE" .'
            }
        }
        stage('Build and lint') {
            steps {
                sh 'docker run --rm "$TEST_IMAGE" python -m compileall -q app.py programs.py tests'
                sh 'docker run --rm "$TEST_IMAGE" ruff check app.py programs.py tests'
            }
        }
        stage('Runtime image') {
            steps { sh 'docker build --target runtime -t "$RUNTIME_IMAGE" .' }
        }
        stage('Containerized tests') {
            steps {
                sh 'docker run --name "$TEST_CONTAINER" "$TEST_IMAGE" python -m pytest -v --junitxml=reports/junit.xml --cov-report=xml:reports/coverage.xml'
                sh '''
                    mkdir -p reports
                    docker cp "$TEST_CONTAINER:/app/reports/." reports/
                '''
            }
        }
        stage('SonarQube Analysis') {
            steps {
                withCredentials([string(credentialsId: 'sonar-token', variable: 'SONAR_TOKEN')]) {
                    sh '''
                        docker rm -f sonar-runner-${BUILD_NUMBER} || true
                        docker create --name sonar-runner-${BUILD_NUMBER} \
                          -e SONAR_HOST_URL="http://host.docker.internal:9000" \
                          -e SONAR_TOKEN="$SONAR_TOKEN" \
                          sonarsource/sonar-scanner-cli
                        docker cp . sonar-runner-${BUILD_NUMBER}:/usr/src
                        docker start -a sonar-runner-${BUILD_NUMBER}
                        docker rm -f sonar-runner-${BUILD_NUMBER} || true
                    '''
                }
            }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker tag "$RUNTIME_IMAGE" "${DOCKER_REPO}:v3.0"
                        docker tag "$RUNTIME_IMAGE" "${DOCKER_REPO}:latest"
                        docker tag "$RUNTIME_IMAGE" "${DOCKER_REPO}:build-${BUILD_NUMBER}"
                        docker push "${DOCKER_REPO}:v3.0"
                        docker push "${DOCKER_REPO}:latest"
                        docker push "${DOCKER_REPO}:build-${BUILD_NUMBER}"
                    '''
                }
            }
        }
    }
    post {
        always {
            sh 'docker rm -f "$TEST_CONTAINER" || true'
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
            sh 'docker image rm "$TEST_IMAGE" "$RUNTIME_IMAGE" || true'
        }
    }
}