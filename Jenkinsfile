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
            }
        }
    }
    post {
        always {
            sh '''
                mkdir -p reports
                if docker container inspect "$TEST_CONTAINER" >/dev/null 2>&1; then
                    docker cp "$TEST_CONTAINER:/app/reports/." reports/ || true
                    docker rm -f "$TEST_CONTAINER" || true
                fi
            '''
            junit testResults: 'reports/junit.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
            sh 'docker image rm "$TEST_IMAGE" "$RUNTIME_IMAGE" || true'
        }
    }
}
