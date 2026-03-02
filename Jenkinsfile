pipeline {
    agent any

    parameters {
        booleanParam(name: 'ROLLBACK_ONLY', defaultValue: false, description: 'Если true — пропустить Test/Build и сделать rollback')
    }

    environment {
        IMAGE_NAME = 'report-service'
        CONTAINER  = 'report-service'
        HEALTH_URL = 'http://localhost:8081/health'
        LAST_FILE  = 'last_successful_build.txt'
    }

    stages {

        stage('Rollback only') {
            when { expression { params.ROLLBACK_ONLY } }
            steps {
                script {
                    if (!fileExists(env.LAST_FILE)) {
                        error("Rollback невозможен: нет ${env.LAST_FILE}. Сначала сделай 1 успешную сборку.")
                    }

                    def prev = readFile(env.LAST_FILE).trim()
                    if (!prev) {
                        error("Rollback невозможен: ${env.LAST_FILE} пустой.")
                    }

                    sh """
                        # Останавливаем старый контейнер (если есть)
                        docker stop ${env.CONTAINER} || true
                        docker rm ${env.CONTAINER} || true

                        # Запускаем предыдущую версию
                        docker run -d -p 8081:5000 --name ${env.CONTAINER} ${env.IMAGE_NAME}:${prev}

                        # Проверяем, что сервис жив
                        curl -f ${env.HEALTH_URL}
                    """
                }
            }
        }

        stage('Test') {
            when { expression { !params.ROLLBACK_ONLY } }
            steps {
                sh """
                    # Создаем виртуальное окружение
                    python3 -m venv venv
                    . venv/bin/activate

                    # Устанавливаем зависимости
                    pip install -r requirements.txt

                    # Запускаем тесты
                    pytest
                """
            }
        }

        stage('Build') {
            when { expression { !params.ROLLBACK_ONLY } }
            steps {
                sh """
                    # Собираем Docker image с тегом BUILD_NUMBER
                    docker build -t ${env.IMAGE_NAME}:${env.BUILD_NUMBER} .
                """
            }
        }

        stage('Deploy') {
            when { expression { !params.ROLLBACK_ONLY } }
            steps {
                sh """
                    # Останавливаем старый контейнер (если есть)
                    docker stop ${env.CONTAINER} || true
                    docker rm ${env.CONTAINER} || true

                    # Запускаем новый контейнер
                    docker run -d -p 8081:5000 --name ${env.CONTAINER} ${env.IMAGE_NAME}:${env.BUILD_NUMBER}
                """
            }
        }

        stage('Health-check') {
            when { expression { !params.ROLLBACK_ONLY } }
            steps {
                script {
                    try {
                        sh "curl -f ${env.HEALTH_URL}"

                        // Если всё хорошо — сохраняем текущую версию как последнюю успешную
                        writeFile(file: env.LAST_FILE, text: "${env.BUILD_NUMBER}\n")
                        echo "Успешно. Сохранили последнюю версию: ${env.BUILD_NUMBER}"

                    } catch (e) {
                        echo "Health-check упал → делаем rollback"

                        if (fileExists(env.LAST_FILE)) {
                            def prev = readFile(env.LAST_FILE).trim()

                            if (prev) {
                                sh """
                                    # Останавливаем сломанную версию
                                    docker stop ${env.CONTAINER} || true
                                    docker rm ${env.CONTAINER} || true

                                    # Запускаем предыдущую версию
                                    docker run -d -p 8081:5000 --name ${env.CONTAINER} ${env.IMAGE_NAME}:${prev}

                                    # Проверяем, что после rollback сервис жив
                                    curl -f ${env.HEALTH_URL}
                                """
                            } else {
                                echo "Rollback невозможен: файл пустой"
                            }
                        } else {
                            echo "Rollback невозможен: файла ${env.LAST_FILE} нет"
                        }

                        // По заданию: после rollback пайплайн должен быть FAILED
                        error("Pipeline FAILED: health-check упал, rollback выполнен (или попытка выполнена).")
                    }
                }
            }
        }
    }
}