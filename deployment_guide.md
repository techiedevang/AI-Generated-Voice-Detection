# Cloud Deployment Guide

This guide explains how to deploy the Voice Detection API to AWS (Elastic Beanstalk) and Google Cloud Platform (Cloud Run).

## Prerequisites
- Docker installed and running locally (for verifying the image).
- AWS CLI or Google Cloud SDK installed.
- An account on AWS or GCP.

---

## 1. The Easiest Way (No Local Installation)

Since you don't have Docker/GCloud installed locally, follow this **GitHub Method**:

1.  **Push Code to GitHub**:
    -   Create a new repository on [GitHub.com](https://github.com/new).
    -   Upload all your files (drag and drop or use Git Bash) to this repo.
    -   *Note*: A `.gitignore` has been added to exclude temporary files.

2.  **Go to Google Cloud Run**:
    -   Open [Google Cloud Console](https://console.cloud.google.com/run).
    -   Click **"Create Service"**.
    -   Select **"Deploy from Repository"**.
    -   Click "Set up with Cloud Build" and connect your GitHub account.
    -   Select your new repository.

3.  **Configure**:
    -   Region: `us-central1` (or nearest).
    -   Authentication: "Allow unauthenticated invocations" (so you can test it).
    -   CPU/Memory: Set to **1 vCPU** and **1GB RAM**.

4.  **Click Create**: Google will automatically build your Docker container and give you a URL!

---

## 2. Local Container Build (Requires Docker Installed)

```bash
# Build the image
docker build -t voice-detection-api .

# Run locally to test
docker run -p 8000:8000 voice-detection-api
```
Tests via `curl` or Postman at `http://localhost:8000/`.

---

## 2. Deploy to AWS (Elastic Beanstalk)

Elastic Beanstalk (EB) is the easiest way to deploy Docker containers on AWS.

1.  **Initialize EB**:
    ```bash
    eb init -p docker voice-detection-api
    ```
    - Select your region (e.g., `us-east-1`).
    - Choose "Docker" as the platform.

2.  **Create Environment**:
    ```bash
    eb create voice-detection-env
    ```
    - This provisions EC2 instances and sets up the load balancer.

3.  **Deploy**:
    ```bash
    eb deploy
    ```

4.  **Access**:
    Get the URL via `eb open` or check the AWS Console.

---

## 3. Deploy to AWS (ECS Fargate) - Alternative

For serverless container management:

1.  **Push to ECR**:
    - Create a repository in Amazon ECR.
    - Tag and push your local image:
      ```bash
      aws ecr get-login-password | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.<region>.amazonaws.com
      docker tag voice-detection-api <repo_uri>:latest
      docker push <repo_uri>:latest
      ```

2.  **Create Task Definition**:
    - In ECS Console, create a new Task Definition (Fargate type).
    - Add container, reference the ECR image URI.
    - Set CPU (e.g., 0.5 vCPU) and Memory (1 GB).

3.  **Run Service**:
    - Create a Cluster.
    - running a Service using the Task Definition.

---

## 4. Deploy to Google Cloud (Cloud Run)

Cloud Run is a fully managed serverless platform for containers.

1.  **Authenticate**:
    ```bash
    gcloud auth login
    gcloud config set project [PROJECT_ID]
    ```

2.  **Enable Services**:
    ```bash
    gcloud services enable cloudbuild.googleapis.com run.googleapis.com
    ```

3.  **Deploy (One Command)**:
    This command builds the image using Cloud Build and deploys it to Cloud Run.
    ```bash
    gcloud run deploy voice-detection-api --source .
    ```
    - Choose a region (e.g., `us-central1`).
    - Allow unauthenticated invocations (if you want it public).

4.  **Access**:
    The command will output a Service URL (e.g., `https://voice-detection-api-xyz.a.run.app`).


---

## 5. Deploy to Render (Recommended Free/Easy Option)

Render is great because it supports Docker natively, which solves the "Install FFmpeg" problem automatically.

1.  **Push to GitHub**:
    -   Ensure your code matches the structure in this folder.
    -   Commit and push to a GitHub repository.

2.  **Create New Service**:
    -   Go to [dashboard.render.com](https://dashboard.render.com/).
    -   Click **New +** -> **Web Service**.
    -   Connect your GitHub repository.

3.  **Configure Settings**:
    -   **Name**: `voice-detection-api`
    -   **Runtime**: Select **Docker** (Critical Step! Do not select Python).
    -   **Instance Type**: Free (or Starter).
    -   **Environment Variables**:
        -   Add `PYTHONUNBUFFERED` = `1` (optional, helps logs).

4.  **Deploy**:
    -   Click **Create Web Service**.
    -   Render will detect the `Dockerfile`, build it (this takes ~5 mins), and start the server.

5.  **Access**:
    -   Render provides a URL like `https://voice-detection-api.onrender.com`.
    -   Use this URL in your `send_mp3.py` (update `API_URL`).

- **Model File**: The `Dockerfile` copies `model.pkl` into the image. Ensure you run `python train_model.py` locally *before* building the image so the model file exists.
- **Performance**: Audio processing with `librosa` and `ffmpeg` can be CPU intensive. On Cloud Run/Fargate, assign at least 1 vCPU and 1GB RAM.
