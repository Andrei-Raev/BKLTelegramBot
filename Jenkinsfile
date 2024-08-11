@Library('TelegramBot@main') _

import com.telebot.TelegramBot

def telegramBot

pipeline {
    agent any

    environment {
        SERVER_USER = 'BKLTelegramBot'
        SERVER_IP = '31.128.44.113'
        SERVER_PATH = '/home/BKLTelegramBot/'
        SSH_KEY = 'ssh_BKLTelegramBot'

        TELEGRAM_TOKEN = '6237067477:AAGzV5LFC_UH9Brp22-TwUvXNsciDK7Nkes'
        TELEGRAM_CHAT_ID = 780828132
    }

    stages {
        stage('Создание уведомления') {
            steps {
                script {
                    telegramBot = new TelegramBot(env.TELEGRAM_CHAT_ID, env.TELEGRAM_TOKEN)
                    telegramBot.updateInfo(updateInfo())

                    telegramBot.addStep("Клонирование репозитория")
                    telegramBot.addStep("Построение Docker образа")
                    telegramBot.addStep("Загрузка файлов на сервер")
                    telegramBot.addStep("Сборка и запуск контейнеров")

                    telegramBot.init()
                }
            }
        }

        stage('Клонирование репозитория') {
            steps {
                script { telegramBot.begin() }

                git branch: 'master', url: 'https://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@github.com/Andrei-Raev/BKLTelegramBot.git'

                script { telegramBot.end() }
            }
        }

        stage('Построение Docker образа') {
            steps {
                script { telegramBot.begin() }

                script {
                    sh 'dos2unix requirements.txt'
                    sh 'docker build -t python-telebot-app .'
                }

                script { telegramBot.end() }
            }
        }

        stage('Загрузка файлов на сервер') {
            steps {
                script { telegramBot.begin() }

                script {
                    withCredentials([sshUserPrivateKey(credentialsId: env.SSH_KEY, keyFileVariable: 'SSH_KEY_PATH')]) {
                        sh """
                        ssh -i ${SSH_KEY_PATH} ${SERVER_USER}@${SERVER_IP} <<EOF
                            docker rm -f python-telebot-app
EOF
                        """
                    }
                }

                script {
                    withCredentials([sshUserPrivateKey(credentialsId: env.SSH_KEY, keyFileVariable: 'SSH_KEY_PATH')]) {
                        sh 'docker save python-telebot-app | bzip2 | pv | ssh -i ${SSH_KEY_PATH} ${SERVER_USER}@${SERVER_IP} "bunzip2 | docker load"'
                    }
                }

                script { telegramBot.end() }
            }
        }

        stage('Сборка и запуск контейнеров') {
            steps {
                script { telegramBot.begin() }

                script {
                    withCredentials([sshUserPrivateKey(credentialsId: env.SSH_KEY, keyFileVariable: 'SSH_KEY_PATH')]) {
                        sh """
                        ssh -i ${SSH_KEY_PATH} ${SERVER_USER}@${SERVER_IP} <<EOF
                            docker start python-telebot-app
                            docker image prune -f
EOF
                        """
                    }

                    sh 'docker image prune -f'
                }

                script { telegramBot.end() }
            }
        }
    }

    post {
        success {
            script {
                telegramBot.updateInfoExtra(updateInfoExtra())
                telegramBot.success()
            }
        }
        failure {
            script {
                telegramBot.updateInfoExtra(updateInfoExtra())
                telegramBot.fail()
            }
        }
    }
}
