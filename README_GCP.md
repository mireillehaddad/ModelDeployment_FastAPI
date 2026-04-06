project churn-predictions-489921, region northamerica-northeast1, repository churn-repo, configured Docker auth, and successfully pushed a container there.

Below is the exact step-by-step flow to do now, assuming you are in Codespaces / bash and your FastAPI project is already working locally in Docker.

0) What you already have

You already finished:

local FastAPI app
Dockerfile
local Docker build
local Docker run on port 9696

So now the GCP part is:

local image → Artifact Registry → Cloud Run

Cloud Run can deploy directly from container images in Artifact Registry, and Google recommends Artifact Registry for this workflow.

1) Open your FastAPI project folder

Go to your FastAPI repo folder:

cd /workspaces/ModelDeployment_FastAPI

Check that these files are present:

ls

You should see things like:

predict.py
model.bin
Dockerfile
pyproject.toml
uv.lock
2) Make sure Docker still works locally

Before deploying to GCP, rebuild and test locally one last time.

Build:

docker build -t fastapi-churn .

Run:

docker run --rm -p 9696:9696 fastapi-churn

Open another terminal and test:

curl http://localhost:9696/docs

If your /predict endpoint is ready, test it too:

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

If local Docker works, move on.

3) Authenticate to Google Cloud

Since you already used a service account for the earlier Flask project, first check who is currently authenticated:

gcloud auth list

Then check the active project:

gcloud config list

Set the project explicitly to the one you already used:

gcloud config set project churn-predictions-489921

Your earlier setup used this project ID.

Check again:

gcloud config get-value project

It should return:

churn-predictions-489921
4) Make sure the needed services are enabled

Because this is the same project, these may already be enabled. Your earlier notes show you had to enable Cloud Resource Manager, Service Usage, Cloud Run, and Artifact Registry-related services in this project.

Run this safely anyway:

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com

Cloud Run deployments rely on Cloud Run and Artifact Registry, and Docker auth/push flows are documented through Artifact Registry.

If it says some are already enabled, that is fine.

5) Reuse your existing Artifact Registry repository

Your previous deployment created this Docker repository:

churn-repo
in region northamerica-northeast1

Verify it exists:

gcloud artifacts repositories list --location=northamerica-northeast1

You should see churn-repo.

If for some reason it is missing, recreate it:

gcloud artifacts repositories create churn-repo \
  --repository-format=docker \
  --location=northamerica-northeast1 \
  --description="Docker repo for churn API"

Artifact Registry repositories can hold multiple images and tags, so you can keep using the same repository for this new FastAPI app.

6) Configure Docker authentication for Artifact Registry

You already did this before, but it is safe to run again:

gcloud auth configure-docker northamerica-northeast1-docker.pkg.dev

Say Y if prompted.

Google’s Artifact Registry docs use this command to let Docker push to the regional registry hostname.

7) Choose names for this new FastAPI deployment

To avoid overwriting your old Flask service, use a different image name and different Cloud Run service name.

Use these:

image name: fastapi-churn
tag: v1
service name: fastapi-churn-api

Now define the full image path:

export PROJECT_ID=churn-predictions-489921
export REGION=northamerica-northeast1
export IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:v1

Check it:

echo $IMAGE

You should see:

northamerica-northeast1-docker.pkg.dev/churn-predictions-489921/churn-repo/fastapi-churn:v1
8) Build the Docker image with the GCP tag

Now build using the Artifact Registry tag directly:

docker build -t $IMAGE .

This creates a local image already named for its GCP destination.

If it finishes successfully, continue.

9) Push the image to Artifact Registry

Push it:

docker push $IMAGE

If successful, the image is now stored in GCP.

You can verify:

gcloud artifacts docker images list $REGION-docker.pkg.dev/$PROJECT_ID/churn-repo

Artifact Registry supports the LOCATION-docker.pkg.dev/PROJECT-ID/REPOSITORY/IMAGE:TAG naming format for images.

10) Deploy the image to Cloud Run

Now deploy it as a new Cloud Run service.

Your app listens on:

host 0.0.0.0
port 9696

That matches Cloud Run’s requirement that the container listen on the configured port, and Cloud Run can expose a public service using --no-invoker-iam-check.

Run:

gcloud run deploy fastapi-churn-api \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --port 9696 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --no-invoker-iam-check

What each part means:

fastapi-churn-api = Cloud Run service name
--image $IMAGE = use the image you pushed
--region $REGION = Montréal
--platform managed = serverless Cloud Run
--port 9696 = your container listens on 9696
--memory 1Gi = enough room for model loading
--cpu 1 = one CPU
--timeout 300 = up to 5 minutes per request
--no-invoker-iam-check = make it public

For new public services, Google documents --no-invoker-iam-check on gcloud run deploy.

11) Copy the Cloud Run URL

After deployment, Cloud Run prints a URL.

It will look similar to:

https://fastapi-churn-api-xxxxx-uc.a.run.app

If you miss it, retrieve it with:

gcloud run services describe fastapi-churn-api \
  --region $REGION \
  --format='value(status.url)'

Cloud Run returns a service URL after successful deployment.

Save it:

export SERVICE_URL=$(gcloud run services describe fastapi-churn-api \
  --region $REGION \
  --format='value(status.url)')

Check it:

echo $SERVICE_URL
12) Test the live service in the browser

Open:

$SERVICE_URL/docs

For example:

https://fastapi-churn-api-xxxxx-uc.a.run.app/docs

You should see FastAPI Swagger docs.

13) Test the live /predict endpoint

Run:

curl -X POST "$SERVICE_URL/predict" \
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

If all is working, you should get your prediction JSON back from the public Cloud Run service.

14) If deployment fails, read the logs

If Cloud Run says the container did not start, the most common causes are:

model.bin not found
dependency problem
app crashed at startup
wrong port

Read logs with:

gcloud run services logs read fastapi-churn-api --region $REGION

Cloud Run logs are available in Cloud Logging and are the first place to check startup failures.

15) Important IAM note

Since January 2025, the principal creating or updating a Cloud Run service needs permission to access the container image in Artifact Registry; Google calls out roles/artifactregistry.reader on the project or repository for the deployer when using Artifact Registry.

So if deployment fails with an image permission error, it means the account you are using to deploy needs access to read that image.

Because your earlier setup used a service account with strong permissions for Cloud Run and Artifact Registry, you may already be covered.

16) After manual deploy works, set up auto-deploy from GitHub

Do this only after the manual deployment succeeds.

Create a file named cloudbuild.yaml in the root of your repo:

steps:
  - name: 'gcr.io/cloud-builders/docker'
    args:
      [
        'build',
        '-t',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:$COMMIT_SHA',
        '.'
      ]

  - name: 'gcr.io/cloud-builders/docker'
    args:
      [
        'push',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:$COMMIT_SHA'
      ]

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      [
        'run',
        'deploy',
        'fastapi-churn-api',
        '--image',
        'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:$COMMIT_SHA',
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
  - 'northamerica-northeast1-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:$COMMIT_SHA'

Cloud Build uses a cloudbuild.yaml file in your project root, and GitHub triggers can run it on pushes.

Push it:

git add cloudbuild.yaml
git commit -m "Add Cloud Build deploy pipeline"
git push

Then in Google Cloud Console:

go to Cloud Build
open Triggers
create a trigger
connect your GitHub repo
choose push to branch
use branch regex: ^main$
build config file: cloudbuild.yaml

Cloud Build supports GitHub triggers for pushes and pull requests.

17) Minimal command list if you want just the exact sequence

Run these one by one from your FastAPI repo:

cd /workspaces/ModelDeployment_FastAPI

gcloud config set project churn-predictions-489921

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  logging.googleapis.com

gcloud artifacts repositories list --location=northamerica-northeast1

gcloud auth configure-docker northamerica-northeast1-docker.pkg.dev

export PROJECT_ID=churn-predictions-489921
export REGION=northamerica-northeast1
export IMAGE=$REGION-docker.pkg.dev/$PROJECT_ID/churn-repo/fastapi-churn:v1

docker build -t $IMAGE .

docker push $IMAGE

gcloud run deploy fastapi-churn-api \
  --image $IMAGE \
  --region $REGION \
  --platform managed \
  --port 9696 \
  --memory 1Gi \
  --cpu 1 \
  --timeout 300 \
  --no-invoker-iam-check

gcloud run services describe fastapi-churn-api \
  --region $REGION \
  --format='value(status.url)'
18) What I recommend you do right now

Do only up to manual deploy first:

build
push
deploy
open /docs
test /predict

Once that works, do the GitHub trigger.

If you hit an error on any command, paste the exact terminal output and I’ll walk through it from that exact point.