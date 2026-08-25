pipeline {

    agent any

    options {
        skipDefaultCheckout(true)
        timestamps()
    }

    environment {
        AWS_REGION     = 'us-east-1'
        ECR_REPOSITORY = 'python-registration'
        EKS_CLUSTER    = 'eksdemo'
    }

    stages {

        // ============================================================
        // 1. CHECKOUT
        // ============================================================

        stage('Checkout') {
            steps {
                checkout scm

                sh '''
                    echo "========================================"
                    echo "Git Information"
                    echo "========================================"

                    echo "Current Branch:"
                    git branch --show-current

                    echo "Current Commit:"
                    git rev-parse --short HEAD

                    echo "Git Remote:"
                    git remote -v

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 2. CONFIGURE AWS
        // ============================================================

        stage('Configure AWS') {
            steps {
                sh '''
                    echo "========================================"
                    echo "AWS Information"
                    echo "========================================"

                    echo "AWS Identity:"
                    aws sts get-caller-identity

                    echo ""
                    echo "Checking EKS Cluster: ${EKS_CLUSTER}"

                    aws eks describe-cluster \
                        --region ${AWS_REGION} \
                        --name ${EKS_CLUSTER} \
                        --query "cluster.status" \
                        --output text

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 3. SET IMAGE VARIABLES
        // ============================================================

        stage('Set Image Variables') {
            steps {
                script {

                    def accountId = sh(
                        script: '''
                            aws sts get-caller-identity \
                                --query Account \
                                --output text
                        ''',
                        returnStdout: true
                    ).trim()

                    def imageTag = sh(
                        script: '''
                            git rev-parse --short=7 HEAD
                        ''',
                        returnStdout: true
                    ).trim()

                    env.ACCOUNT_ID = accountId

                    env.ECR_REGISTRY =
                        "${accountId}.dkr.ecr.${env.AWS_REGION}.amazonaws.com"

                    env.IMAGE_TAG = imageTag

                    echo "========================================"
                    echo "Image Information"
                    echo "========================================"
                    echo "AWS Account : ${env.ACCOUNT_ID}"
                    echo "ECR Registry: ${env.ECR_REGISTRY}"
                    echo "Repository  : ${env.ECR_REPOSITORY}"
                    echo "Image Tag   : ${env.IMAGE_TAG}"
                    echo "Full Image  : ${env.ECR_REGISTRY}/${env.ECR_REPOSITORY}:${env.IMAGE_TAG}"
                    echo "========================================"
                }
            }
        }


        // ============================================================
        // 4. LOGIN TO ECR
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

                    echo "ECR login completed successfully."

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 5. SELECT ENVIRONMENT
        // ============================================================

        stage('Select Environment') {
            steps {
                script {

                    def branch = env.BRANCH_NAME

                    echo "========================================"
                    echo "Environment Selection"
                    echo "========================================"
                    echo "Building Branch: ${branch}"

                    if (branch == 'dev') {

                        env.NAMESPACE = 'dev'
                        env.VALUES_FILE = 'values-dev.yaml'

                    } else if (branch == 'stage') {

                        env.NAMESPACE = 'stage'
                        env.VALUES_FILE = 'values-stage.yaml'

                    } else if (branch == 'prod') {

                        env.NAMESPACE = 'prod'
                        env.VALUES_FILE = 'values-prod.yaml'

                    } else {

                        error(
                            "Unsupported branch: ${branch}. " +
                            "Only dev, stage and prod are supported."
                        )
                    }

                    echo "Namespace  : ${env.NAMESPACE}"
                    echo "Values File: ${env.VALUES_FILE}"
                    echo "========================================"
                }
            }
        }


        // ============================================================
        // 6. VERIFY ECR REPOSITORY
        // ============================================================

        stage('Verify ECR Repository') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Checking ECR Repository"
                    echo "========================================"

                    aws ecr describe-repositories \
                        --region ${AWS_REGION} \
                        --repository-names ${ECR_REPOSITORY}

                    echo "ECR repository exists."

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 7. BUILD DOCKER IMAGE
        // ============================================================

        stage('Build Docker Image') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Building Docker Image"
                    echo "========================================"

                    docker build \
                        -t ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG} \
                        .

                    echo ""
                    echo "Docker image built successfully."

                    docker images | grep ${ECR_REPOSITORY} || true

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 8. PUSH DOCKER IMAGE TO ECR
        // ============================================================

        stage('Push Docker Image') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Pushing Docker Image to ECR"
                    echo "========================================"

                    docker push \
                        ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

                    echo ""
                    echo "Docker image pushed successfully."

                    echo "Image:"
                    echo "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 9. CONFIGURE KUBERNETES
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

                    echo ""
                    echo "Kubernetes Cluster:"
                    kubectl cluster-info

                    echo ""
                    echo "Kubernetes Nodes:"
                    kubectl get nodes

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 10. HELM LINT
        // ============================================================

        stage('Helm Lint') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Helm Lint"
                    echo "========================================"

                    helm lint \
                        ./helm/python-registration

                    echo "Helm lint completed successfully."

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 11. HELM DEPLOYMENT
        // ============================================================

        stage('Deploy with Helm') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Deploying Application"
                    echo "========================================"

                    echo "Cluster  : ${EKS_CLUSTER}"
                    echo "Namespace: ${NAMESPACE}"
                    echo "Values   : ${VALUES_FILE}"
                    echo "Image    : ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"

                    helm upgrade --install \
                        python-registration \
                        ./helm/python-registration \
                        --namespace ${NAMESPACE} \
                        --create-namespace \
                        -f ./helm/python-registration/${VALUES_FILE} \
                        --set pythonApp.image.repository=${ECR_REGISTRY}/${ECR_REPOSITORY} \
                        --set pythonApp.image.tag=${IMAGE_TAG}

                    echo ""
                    echo "Helm deployment completed."

                    echo "========================================"
                '''
            }
        }


        // ============================================================
        // 12. VERIFY DEPLOYMENT
        // ============================================================

        stage('Verify Deployment') {
            steps {
                sh '''
                    echo "========================================"
                    echo "Deployment Verification"
                    echo "========================================"

                    echo ""
                    echo "===== PODS ====="
                    kubectl get pods \
                        -n ${NAMESPACE} \
                        -o wide

                    echo ""
                    echo "===== SERVICES ====="
                    kubectl get svc \
                        -n ${NAMESPACE}

                    echo ""
                    echo "===== DEPLOYMENTS ====="
                    kubectl get deployments \
                        -n ${NAMESPACE}

                    echo ""
                    echo "===== REPLICASETS ====="
                    kubectl get replicasets \
                        -n ${NAMESPACE}

                    echo ""
                    echo "===== ROLLOUT STATUS ====="

                    kubectl rollout status \
                        deployment/python-app \
                        -n ${NAMESPACE} \
                        --timeout=180s

                    echo ""
                    echo "===== FINAL POD STATUS ====="

                    kubectl get pods \
                        -n ${NAMESPACE}

                    echo ""
                    echo "Deployment verification completed."

                    echo "========================================"
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
Cluster   : ${env.EKS_CLUSTER}
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
Cluster   : ${env.EKS_CLUSTER}

========================================
"""
        }

        always {
            sh '''
                if [ -n "${ECR_REGISTRY}" ]; then
                    docker logout "${ECR_REGISTRY}" || true
                fi
            '''
        }
    }
}
