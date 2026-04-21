# Automated Docker Image Deployment to AWS ECR with Jenkins & Lambda

##  Project Overview

This project implements a complete **CI/CD pipeline** that:

* Builds a Docker image using Jenkins
* Pushes the image to Amazon ECR
* Triggers AWS Lambda via EventBridge
* Stores metadata in DynamoDB
* Sends notification via SNS

---

##  Architecture

```
Jenkins → Docker Build → Amazon ECR → EventBridge → AWS Lambda → DynamoDB + SNS
```

---

## Technologies Used

* Jenkins (CI/CD)
* Docker
* AWS ECR (Elastic Container Registry)
* AWS Lambda
* AWS DynamoDB
* AWS SNS (Simple Notification Service)
* AWS IAM

---

##  Prerequisites

* AWS Account
* Jenkins installed on EC2
* Docker installed
* AWS CLI configured
* IAM role with required permissions

---

## 📦 Step 1: Docker Setup

### Sample Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
```

---

## 🔄 Step 2: Jenkins Pipeline

### Jenkinsfile

```
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        AWS_REGION = "us-east-1"
        ACCOUNT_ID = "492711554489"
        ECR_REPO = "devops-demo"
        IMAGE_TAG = "latest"
        ECR_URI = "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/iamsakshimore/docker-ecr-jenkins-lambda-python-app.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t devops-demo:latest .'
            }
        }

        stage('Login to ECR') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'aws-creds',
                    usernameVariable: 'AWS_ACCESS_KEY_ID',
                    passwordVariable: 'AWS_SECRET_ACCESS_KEY'
                )]) {
                    sh '''
                    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
                    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

                    aws ecr get-login-password --region $AWS_REGION | \
                    docker login --username AWS \
                    --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com
                    '''
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh '''
                docker tag devops-demo:latest \
                $ECR_URI:$IMAGE_TAG
                '''
            }
        }

        stage('Push to ECR') {
            steps {
                sh '''
                docker push $ECR_URI:$IMAGE_TAG
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Image pushed successfully → Lambda will trigger via EventBridge"
        }
        failure {
            echo "❌ Pipeline failed — check logs"
        }
    }
}

```

---

## ⚡ Step 3: AWS Lambda Function

### Python Code

```python
`

## 🗄️ Step 4: DynamoDB Configuration

* Table Name: `ImageLogs`
* Partition Key: `image_tag` (String)

---

## 📡 Step 5: SNS Notification

1. Create SNS Topic
2. Add Email Subscription
3. Confirm Email
4. Add Topic ARN in Lambda

---

## 🔔 Step 6: EventBridge Rule

* Source: `aws.ecr`
* Event Type: Image Push
* Target: Lambda Function

---

## 🔐 IAM Permissions Required

### Lambda Role:

* DynamoDB: `PutItem`
* SNS: `Publish`

### Jenkins IAM User:

* ECR Full Access (or limited required actions)

---

## 🧪 Testing

1. Commit code → Jenkins triggers build
2. Image pushed to ECR
3. Lambda triggered automatically
4. Data stored in DynamoDB
5. Email notification received

---

## ❗ Common Issues & Fixes

| Issue                    | Fix                          |
| ------------------------ | ---------------------------- |
| Docker permission denied | Add user to docker group     |
| ECR push fails           | Configure AWS credentials    |
| DynamoDB error           | Ensure `image_tag` is String |
| No notification          | Confirm SNS email            |

---

## 🎯 Outcome

* Fully automated CI/CD pipeline
* Real-time event-driven processing
* Logging + notifications


