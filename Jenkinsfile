pipeline {
  agent any

  parameters {
    booleanParam(name: 'ROLLBACK_ONLY', defaultValue: false, description: '')
  }

  stages {
    stage('Rollback') {
      when { expression { params.ROLLBACK_ONLY } }
      steps {
        script {
          if (!fileExists('last_successful_build.txt')) { error('Rollback невозможен') }
          def prev = readFile('last_successful_build.txt').trim()
          if (!prev) { error('Rollback невозможен') }
          sh """
            docker stop report-service || true
            docker rm report-service || true
            docker run -d -p 8081:5000 --name report-service report-service:${prev}
            curl -f http://localhost:8081/health
          """
        }
      }
    }

    stage('Test') {
      when { expression { !params.ROLLBACK_ONLY } }
      steps {
        sh """
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install "Werkzeug<3"
          pytest
        """
      }
    }

    stage('Build') {
      when { expression { !params.ROLLBACK_ONLY } }
      steps {
        sh "docker build -t report-service:${BUILD_NUMBER} ."
      }
    }

    stage('Deploy') {
      when { expression { !params.ROLLBACK_ONLY } }
      steps {
        sh """
          docker stop report-service || true
          docker rm report-service || true
          docker run -d -p 8081:5000 --name report-service report-service:${BUILD_NUMBER}
        """
      }
    }

    stage('Health-check') {
      when { expression { !params.ROLLBACK_ONLY } }
      steps {
        script {
          try {
            sh "curl -f http://localhost:8081/health"
            writeFile(file: 'last_successful_build.txt', text: "${BUILD_NUMBER}\n")
          } catch (e) {
            if (fileExists('last_successful_build.txt')) {
              def prev = readFile('last_successful_build.txt').trim()
              if (prev) {
                sh """
                  docker stop report-service || true
                  docker rm report-service || true
                  docker run -d -p 8081:5000 --name report-service report-service:${prev}
                  curl -f http://localhost:8081/health
                """
              }
            }
            error('FAILED')
          }
        }
      }
    }
  }
}