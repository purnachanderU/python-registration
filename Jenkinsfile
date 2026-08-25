pipeline {

    agent any

    environment {

        AWS_REGION     = 'us-east-1'
        ECR_REPOSITORY = 'python-registration'
        EKS_CLUSTER    = 'eksdemo'

        ECR_REGISTRY = ''
        IMAGE_TAG    = ''
        NAMESPACE    = ''
        VALUES_FILE  = ''
    }

    stages {

        // ============================================================
        // 1. Checkout
        // ============================================================

        stage('Checkout') {

            steps {

                checkout scm

                sh '''
                    echo "========================================"
                    echo "Current Branch"
                    echo "========================================"

                    git branch --show-current

                    echo "========================================"
                    echo "Current Commit"
                    echo "========================================"

                    git rev-parse --short HEAD
                '''
            }
        }


        // ============================================================
        // 2. Configure AWS
        // ============================================================

        stage('Configure AWS') {

            steps {

                sh '''
                    echo "========================================"
                    echo "AWS Identity"
                    echo "========================================"

                    aws sts get-caller-identity

                    echo "========================================"
                    echo "Checking EKS Cluster"
                    echo "========================================"

                    aws eks describe-cluster \
                      --region ${AWS_REGION} \
                      --name ${EKS_CLUSTER} \
                      --query "cluster.status" \
                      --output text
                '''
            }
        }


        // ============================================================
        // 3. Set Image Variables
        // ============================================================

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


                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()


                    echo "========================================"
                    echo "Image Information"
                    echo "========================================"

                    echo "AWS Account : ${env.ACCOUNT_ID}"
                    echo "ECR Registry: ${env.ECR_REGISTRY}"
                    echo "Repository  : ${env.ECR_REPOSITORY}"
                    echo "Image Tag   : ${env.IMAGE_TAG}"
                }
            }
        }


        // ============================================================
        // 4. Login to ECR
        // ============================================================

        stage('Login to ECR') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Logging into Amazon ECR"
                    echo "========================================"

                    echo "ECR Registry: ${ECR_REGISTRY}"

                    aws ecr get-login-password \
                      --region ${AWS_REGION} | \
                    docker login \
                      --username AWS \
                      --password-stdin \
                      ${ECR_REGISTRY}
                '''
            }
        }


        // ============================================================
        // 5. Select Environment
        // ============================================================

        stage('Select Environment') {

            steps {

                script {

                    def branch = env.BRANCH_NAME

                    echo "========================================"
                    echo "Deployment Environment"
                    echo "========================================"

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

                        error(
                            "Unsupported branch: ${branch}. " +
                            "Only dev, stage and prod branches are supported."
                        )
                    }


                    echo "Namespace : ${env.NAMESPACE}"
                    echo "Values    : ${env.VALUES_FILE}"
                }
            }
        }


        // ============================================================
        // 6. Build Docker Image
        // ============================================================

        stage('Build Docker Image') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Building Docker Image"
                    echo "========================================"

                    echo "Image:"
                    echo "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"


                    docker build \
                      -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} \
                      .
                '''
            }
        }


        // ============================================================
        // 7. Push Docker Image
        // ============================================================

        stage('Push Docker Image') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Pushing Docker Image to ECR"
                    echo "========================================"

                    docker push \
                      ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}
                '''
            }
        }


        // ============================================================
        // 8. Configure Kubernetes
        // ============================================================

        stage('Configure Kubernetes') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Configuring Kubernetes"
                    echo "========================================"

                    aws eks update-kubeconfig \
                      --region ${AWS_REGION} \
                      --name ${EKS_CLUSTER}


                    echo "========================================"
                    echo "Kubernetes Cluster Info"
                    echo "========================================"

                    kubectl cluster-info
                '''
            }
        }


        // ============================================================
        // 9. Helm Lint
        // ============================================================

        stage('Helm Lint') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Helm Lint"
                    echo "========================================"

                    helm lint ./helm/python-registration
                '''
            }
        }


        // ============================================================
        // 10. Deploy with Helm
        // ============================================================

        stage('Deploy with Helm') {

            steps {

                sh '''
                    echo "========================================"
                    echo "Helm Deployment"
                    echo "========================================"

                    echo "Release   : python-registration"
                    echo "Namespace : ${NAMESPACE}"
                    echo "Values    : ${VALUES_FILE}"
                    echo "Image     : ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"


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


        // ============================================================
        // 11. Verify Deployment
        // ============================================================

        stage('Verify Deployment') {

            steps {

                sh '''
                    echo "========================================"
                    echo "PODS"
                    echo "========================================"

                    kubectl get pods \
                      -n ${NAMESPACE}


                    echo "========================================"
                    echo "SERVICES"
                    echo "========================================"

                    kubectl get svc \
                      -n ${NAMESPACE}


                    echo "========================================"
                    echo "DEPLOYMENTS"
                    echo "========================================"

                    kubectl get deployment \
                      -n ${NAMESPACE}


                    echo "========================================"
                    echo "ROLLOUT STATUS"
                    echo "========================================"

                    kubectl rollout status \
                      deployment/python-app \
                      -n ${NAMESPACE} \
                      --timeout=180s
                '''
            }
        }
    }


    // ================================================================
    // POST ACTIONS
    // ================================================================

    post {

        success {

            echo """
========================================
       DEPLOYMENT SUCCESSFUL
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
         DEPLOYMENT FAILED
========================================

Branch    : ${env.BRANCH_NAME}
Namespace : ${env.NAMESPACE}

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
