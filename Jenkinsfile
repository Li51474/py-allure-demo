pipeline {
    /* 1. 在任何可用节点执行 */
    agent any

    /* 2. 环境变量（按需修改） */
    environment {
        /* Python 可执行文件路径（Linux 用 python3，Windows 用 python） */
        PYTHON = "${isUnix() ? 'python3' : 'python'}"
        /* 虚拟环境目录名 */
        VENV_DIR      = 'venv'
        /* Allure 结果目录（pytest 指定） */
        ALLURE_RESULTS = 'allure-results'
        /* 收件人邮箱（如不需要可删除） */
        EMAIL_TO      = '2149251474@qq.com'
    }

    /* 3. 阶段 */
    stages {
        stage('Checkout') {
            steps {
                /* 自动拉取当前仓库代码 */
                checkout scm
            }
        }

        stage('Create venv & Install deps') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            ${PYTHON} -m venv ${VENV_DIR}
                            . ${VENV_DIR}/bin/activate
                            pip install -r requirements.txt
                        """
                    } else {
                        bat """
                            ${PYTHON} -m venv ${VENV_DIR}
                            call ${VENV_DIR}\\Scripts\\activate
                            pip install -r requirements.txt
                        """
                    }
                }
            }
        }

        stage('Run Pytest + Allure') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV_DIR}/bin/activate
                            pytest --alluredir=${ALLURE_RESULTS}
                        """
                    } else {
                        bat """
                            call ${VENV_DIR}\\Scripts\\activate
                            pytest --alluredir=%ALLURE_RESULTS%
                        """
                    }
                }
            }
        }

        stage('Generate & Publish Allure Report') {
            steps {
                allure([
                    includeProperties: false,
                    jdk              : '',
                    reportBuildPolicy: 'ALWAYS',
                    results          : [[path: "${ALLURE_RESULTS}"]]
                ])
            }
        }
    }

    /* 4. 构建后动作（可选：邮件通知） */
    post {
        always {
            script {
                /* 只在配置了 EMAIL_TO 时发送 */
                if (env.EMAIL_TO?.trim()) {
                    emailext (
                        subject: "[${env.JOB_NAME}] Build #${env.BUILD_NUMBER} - ${currentBuild.result ?: 'SUCCESS'}",
                        body   : """<p>查看 Allure 报告：<a href="${env.BUILD_URL}allure">${env.BUILD_URL}allure</a></p>""",
                        to     : env.EMAIL_TO
                    )
                }
            }
        }
    }
}
