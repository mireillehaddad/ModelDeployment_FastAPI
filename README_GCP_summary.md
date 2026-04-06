# 🚀 FastAPI Model Deployment to GCP (Cloud Run)

## ✅ Project Setup (Already Done)

* Project ID: `churn-predictions-489921`
* Region: `northamerica-northeast1`
* Artifact Registry repo: `churn-repo`
* Local Docker image: `churn-prediction`

---

# 🧩 Step 1 — Open project folder

```bash
cd /workspaces/ModelDeployment_FastAPI
ls
```

Expected files:

* predict.py
* model.bin
* Dockerfile
* pyproject.toml
* uv.lock

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

---

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

```
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

# ✅ DONE

You now have:

* Dockerized ML model
* Image in Artifact Registry
* Deployed API on Cloud Run
* Public endpoint

---

# 🚀 Add CI/CD with `cloudbuild.yaml` for auto-deploy from GitHub.


