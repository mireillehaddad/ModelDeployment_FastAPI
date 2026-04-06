# 🚀 FastAPI Model Deployment to GCP (Cloud Run + CI/CD)

## ✅ Project Setup (Already Done)

- Project ID: `churn-predictions-489921`
- Region: `northamerica-northeast1`
- Artifact Registry repo: `churn-repo`
- Local Docker image: `churn-prediction`

---

# 🧩 Step 1 — Open project folder

```bash
cd /workspaces/ModelDeployment_FastAPI
ls
```

Expected files:
- predict.py
- model.bin
- Dockerfile
- pyproject.toml
- uv.lock

---

# 🐳 Step 2 — Build Docker image

```bash
docker build -t churn-prediction .
```

---

# 🧪 Step 3 — Test locally

```bash
docker run --rm -p 9696:9696 churn-prediction
```

Test:

```bash
curl http://localhost:9696/docs
```

Test prediction:

```bash
curl -X POST "http://localhost:9696/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "seniorcitizen": 0,
    "partner": "no",
    "dependents": "yes",
    "phoneservice": "no",
    "multiplelines": "no_phone_service",
    "internetservice": "dsl",
    "onlinesecurity": "no",
    "onlinebackup": "yes",
    "deviceprotection": "no",
    "techsupport": "no",
    "streamingtv": "no",
    "streamingmovies": "no",
    "contract": "month-to-month",
    "paperlessbilling": "yes",
    "paymentmethod": "electronic_check",
    "tenure": 6,
    "monthlycharges": 29.85,
    "totalcharges": 129.85
  }'
```

---

# ☁️ Step 4 — Set GCP project

```bash
gcloud config set project churn-predictions-489921
gcloud config get-value project
```

---

# ⚙️ Step 5 — Enable services

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com
```

---

# 📦 Step 6 — Check repository

```bash
gcloud artifacts repositories list --location=northamerica-northeast1
```

If missing:

```bash
gcloud artifacts repositories create churn-repo \
  --repository-format=docker \
  --location=northamerica-northeast1 \
  --description="Docker repo for churn API"
```

---

# 🔐 Step 7 — Configure Docker auth

```bash
gcloud auth configure-docker northamerica-northeast1-docker.pkg.dev
```

Type `Y`

---

# 🏷️ Step 8 — Tag image for GCP

```bash
docker tag churn-prediction \
northamerica-northeast1-docker.pkg.dev/churn-predictions-489921/churn-repo/churn-prediction:v1
```

---

# 📤 Step 9 — Push image

```bash
docker push \
northamerica-northeast1-docker.pkg.dev/churn-predictions-489921/churn-repo/churn-prediction:v1
```

---

# 🚀 Step 10 — Deploy to Cloud Run

## ✅ Safe option (new service)

```bash
gcloud run deploy churn-prediction-api \
  --image northamerica-northeast1-docker.pkg.dev/churn-predictions-489921/churn-repo/churn-prediction:v1 \
  --region northamerica-northeast1 \
  --platform managed \
  --port 9696 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --no-invoker-iam-check
```

## ⚠️ Optional (overwrite existing service)

```bash
gcloud run deploy churn-api \
  --image northamerica-northeast1-docker.pkg.dev/churn-predictions-489921/churn-repo/churn-prediction:v1 \
  --region northamerica-northeast1 \
  --platform managed \
  --port 9696 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --no-invoker-iam-check
```

---

# 🔗 Step 11 — Get URL

```bash
gcloud run services describe churn-prediction-api \
  --region northamerica-northeast1 \
  --format='value(status.url)'
```

---

# 🌐 Step 12 — Test deployed API

Open:

```text
https://YOUR_URL/docs
```

Test prediction:

```bash
curl -X POST "YOUR_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

---

# 🧯 Step 13 — Debug

```bash
gcloud run services logs read churn-prediction-api --region northamerica-northeast1
```

---

# 🔁 Step 14 — Add CI/CD with Cloud Build

Cloud Build can use a `cloudbuild.yaml` file in your repo root, and Cloud Build triggers can automatically run builds on GitHub pushes. Cloud Run also supports continuous deployment from a Git repository through Cloud Build.

Create a file named `cloudbuild.yaml` in the root of your repo:

```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      [
        'build',
        '-t',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/churn-prediction:$COMMIT_SHA',
        '.'
      ]

  - name: 'gcr.io/cloud-builders/docker'
    args:
      [
        'push',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/churn-prediction:$COMMIT_SHA'
      ]

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      [
        'run',
        'deploy',
        'churn-prediction-api',
        '--image',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/churn-prediction:$COMMIT_SHA',
        '--region',
        'northamerica-northeast1',
        '--platform',
        'managed',
        '--port',
        '9696',
        '--memory',
        '1Gi',
        '--cpu',
        '1',
        '--timeout',
        '300',
        '--no-invoker-iam-check'
      ]

images:
  - 'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/churn-prediction:$COMMIT_SHA'
```

---

# 📝 Step 15 — Commit and push `cloudbuild.yaml`

```bash
git add cloudbuild.yaml
git commit -m "Add Cloud Build CI/CD pipeline"
git push
```

---

# 🔗 Step 16 — Create the GitHub trigger

In Google Cloud Console:

1. Go to **Cloud Build**
2. Open **Triggers**
3. Click **Create trigger**
4. Connect your GitHub account if needed
5. Select your repository: `ModelDeployment_FastAPI`
6. Event: **Push to a branch**
7. Branch (regex): `^main$`
8. Configuration: **Cloud Build configuration file**
9. Location of config file: `cloudbuild.yaml`
10. Save the trigger

---

# 🧪 Step 17 — Test auto-deploy

Make a small change in your repo, then run:

```bash
git add .
git commit -m "Test auto deploy"
git push
```

That push should trigger:

1. Docker build
2. Docker push to Artifact Registry
3. Cloud Run redeploy

---

# ✅ DONE

You now have:
- Dockerized ML model
- Image in Artifact Registry
- API deployed on Cloud Run
- Public endpoint
- GitHub → Cloud Build → Cloud Run auto-deploy pipeline
