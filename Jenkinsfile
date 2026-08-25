pipeline {

    agent any

    environment {

        AWS_REGION      = 'us-east-1'
        ECR_REPOSITORY  = 'python-registration'
        EKS_CLUSTER     = 'eksdemo'

        ECR_REGISTRY    = ''
        IMAGE_TAG       = ''
        NAMESPACE       = ''
        VALUES_FILE     = ''
    }

    stages {

        // ------------------------------------------------
        // 1. Checkout
        // ------------------------------------------------

        stage('Checkout') {

            steps {

                checkout scm

                sh '''
                    echo "Current branch:"
                    git branch --show-current

                    echo "Current commit:"
                    git rev-parse --short HEAD
                '''
            }
        }


        // ------------------------------------------------
        // 2. Configure AWS
        // ------------------------------------------------

        stage('Configure AWS') {

            steps {

                sh '''
                    aws sts get-caller-identity

                    aws eks describe-cluster \
                      --region ${AWS_REGION} \
                      --name ${EKS_CLUSTER} \
                      --query "cluster.status" \
                      --output text
                '''
            }
        }


        // ------------------------------------------------
        // 3. Login to ECR
        // ------------------------------------------------

        stage('Login to ECR') {
           steps {
              sh '''
                  aws ecr get-login-password --region $AWS_REGION | \
                  docker login \
                  --username AWS \
                  --password-stdin \
                   $ECR_REGISTRY
              '''
           }
        }


        // ------------------------------------------------
        // 4. Set image variables
        // ------------------------------------------------

        stage('Set Image Variables') {

            steps {

                script {

                    env.ACCOUNT_ID = sh(
                        script: '''
                            aws sts get-caller-identity \
                              --query Account \
                              --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    env.ECR_REGISTRY =
                        "${env.ACCOUNT_ID}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"

                    env.IMAGE_TAG =
                        sh(
                            script: 'git rev-parse --short=7 HEAD',
                            returnStdout: true
                        ).trim()

                    echo "ECR Registry: ${env.ECR_REGISTRY}"
                    echo "Repository: ${env.ECR_REPOSITORY}"
                    echo "Image Tag: ${env.IMAGE_TAG}"
                }
            }
        }


        // ------------------------------------------------
        // 5. Select environment
        // ------------------------------------------------

        stage('Select Environment') {

            steps {

                script {

                    def branch = env.BRANCH_NAME

                    echo "Building branch: ${branch}"

                    if (branch == 'dev') {

                        env.NAMESPACE = 'dev'
                        env.VALUES_FILE = 'values-dev.yaml'

                    }
                    else if (branch == 'stage') {

                        env.NAMESPACE = 'stage'
                        env.VALUES_FILE = 'values-stage.yaml'

                    }
                    else if (branch == 'prod') {

                        env.NAMESPACE = 'prod'
                        env.VALUES_FILE = 'values-prod.yaml'

                    }
                    else {

                        error("Unsupported branch: ${branch}")
                    }

                    echo "Namespace: ${env.NAMESPACE}"
                    echo "Values file: ${env.VALUES_FILE}"
                }
            }
        }


        // ------------------------------------------------
        // 6. Build Docker image
        // ------------------------------------------------

        stage('Build Docker Image') {

            steps {

                sh '''
                    docker build \
                      -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} \
                      .
                '''
            }
        }


        // ------------------------------------------------
        // 7. Push Docker image
        // ------------------------------------------------

        stage('Push Docker Image') {

            steps {

                sh '''
                    docker push \
                      ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                '''
            }
        }


        // ------------------------------------------------
        // 8. Configure kubectl
        // ------------------------------------------------

        stage('Configure Kubernetes') {

            steps {

                sh '''
                    aws eks update-kubeconfig \
                      --region ${AWS_REGION} \
                      --name ${EKS_CLUSTER}

                    kubectl cluster-info
                '''
            }
        }


        // ------------------------------------------------
        // 9. Helm lint
        // ------------------------------------------------

        stage('Helm Lint') {

            steps {

                sh '''
                    helm lint ./helm/python-registration
                '''
            }
        }


        // ------------------------------------------------
        // 10. Helm deployment
        // ------------------------------------------------

        stage('Deploy with Helm') {

            steps {

                sh '''
                    helm upgrade --install python-registration \
                      ./helm/python-registration \
                      --namespace ${NAMESPACE} \
                      --create-namespace \
                      -f ./helm/python-registration/${VALUES_FILE} \
                      --set pythonApp.image.repository=${ECR_REGISTRY}/${ECR_REPOSITORY} \
                      --set pythonApp.image.tag=${IMAGE_TAG}
                '''
            }
        }


        // ------------------------------------------------
        // 11. Verify deployment
        // ------------------------------------------------

        stage('Verify Deployment') {

            steps {

                sh '''
                    echo "===== PODS ====="

                    kubectl get pods \
                      -n ${NAMESPACE}

                    echo "===== SERVICES ====="

                    kubectl get svc \
                      -n ${NAMESPACE}

                    echo "===== DEPLOYMENT ====="

                    kubectl get deployment \
                      -n ${NAMESPACE}

                    echo "===== ROLLOUT STATUS ====="

                    kubectl rollout status \
                      deployment/python-app \
                      -n ${NAMESPACE} \
                      --timeout=180s
                '''
            }
        }
    }


    // ------------------------------------------------
    // Post actions
    // ------------------------------------------------

    post {

        success {

            echo """
            ========================================
            Deployment Successful
            ========================================
            Branch    : ${env.BRANCH_NAME}
            Namespace : ${env.NAMESPACE}
            Image     : ${env.ECR_REGISTRY}/${env.ECR_REPOSITORY}:${env.IMAGE_TAG}
            ========================================
            """
        }

        failure {

            echo """
            ========================================
            Deployment Failed
            ========================================
            Branch    : ${env.BRANCH_NAME}
            ========================================
            """
        }

        always {

            sh '''
                docker logout ${ECR_REGISTRY} || true
            '''
        }
    }
}
