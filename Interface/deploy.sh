#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# Setup & Environment
# ----------------------------
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "ERROR: .env file not found in ${ROOT_DIR}"
  exit 1
fi

set -a
source "${ENV_FILE}"
set +a

# List of required variables from .env
required_vars=(
  PROJECT_ID
  SERVICE_NAME
  REGION
  ARTIFACT_REPOSITORY
  IMAGE_NAME
  IMAGE_TAG
  CLOUD_RUN_CPU
  CLOUD_RUN_MEMORY
  CLOUD_RUN_MAX_INSTANCES
  CLOUD_RUN_MIN_INSTANCES
  CLOUD_RUN_CONCURRENCY
  CLOUD_RUN_TIMEOUT
  CLOUD_RUN_PORT
  OPENAI_API_KEY
  NEWS_API_KEY
  GOOGLE_API_KEY
  TAVILY_API_KEY
)

# Validate that all required variables are set
for var in "${required_vars[@]}"; do
  if [[ -z "${!var:-}" ]]; then
    echo "ERROR: Variable ${var} is missing in .env"
    exit 1
  fi
done

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REPOSITORY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo "==> Setting gcloud project to: ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

echo "==> Enabling required APIs (this may take a minute)"
gcloud services enable \
  run.googleapis.com \
  secretmanager.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  iam.googleapis.com \
  generativelanguage.googleapis.com \
  --project="$PROJECT_ID"

# ----------------------------
# Resource Provisioning
# ----------------------------

echo "==> Creating Artifact Registry repository if needed"
gcloud artifacts repositories create "${ARTIFACT_REPOSITORY}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Artifact Registry for news_paper" 2>/dev/null || echo "Repository already exists."

echo "==> Ensuring Firestore database exists (Native Mode)"
gcloud firestore databases create \
    --database="(default)" \
    --location="nam5" \
    --type=firestore-native 2>/dev/null || echo "Firestore database already exists or is being provisioned."

echo "==> Granting Firestore permissions to Cloud Run Service Account"
PROJECT_NUMBER=$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/datastore.user" --quiet >/dev/null

# ----------------------------
# Build & Deploy
# ----------------------------

echo "==> Building container image with Cloud Build"
gcloud builds submit "${ROOT_DIR}" --tag "${IMAGE_URI}"

echo "==> Deploying to Cloud Run: ${SERVICE_NAME}"
# Corrected: Env vars in a single comma-separated string with no spaces
DEPLOY_ARGS=(
  "${SERVICE_NAME}"
  "--image=${IMAGE_URI}"
  "--region=${REGION}"
  "--platform=managed"
  "--port=${CLOUD_RUN_PORT}"
  "--memory=${CLOUD_RUN_MEMORY}"
  "--cpu=${CLOUD_RUN_CPU}"
  "--max-instances=${CLOUD_RUN_MAX_INSTANCES}"
  "--min-instances=${CLOUD_RUN_MIN_INSTANCES}"
  "--concurrency=${CLOUD_RUN_CONCURRENCY}"
  "--timeout=${CLOUD_RUN_TIMEOUT}"
  "--set-env-vars=APP_TITLE=${APP_TITLE},ENVIRONMENT=${ENVIRONMENT},APPLICATION=${APPLICATION},OWNER=${OWNER},PROJECT_ID=${PROJECT_ID},FIRESTORE_DATABASE=${FIRESTORE_DATABASE},FIRESTORE_COLLECTION_USERS=${FIRESTORE_COLLECTION_USERS},FIRESTORE_COLLECTION_AUDIT=${FIRESTORE_COLLECTION_AUDIT},STREAMLIT_SERVER_HEADLESS=${STREAMLIT_SERVER_HEADLESS},STREAMLIT_BROWSER_GATHER_USAGE_STATS=${STREAMLIT_BROWSER_GATHER_USAGE_STATS},OPENAI_API_KEY=${OPENAI_API_KEY},NEWS_API_KEY=${NEWS_API_KEY},GOOGLE_API_KEY=${GOOGLE_API_KEY},TAVILY_API_KEY=${TAVILY_API_KEY},GOOGLE_CLOUD_QUOTA_PROJECT=${PROJECT_ID}"
)

if [[ "${CLOUD_RUN_ALLOW_UNAUTHENTICATED}" == "true" ]]; then
  DEPLOY_ARGS+=("--allow-unauthenticated")
else
  DEPLOY_ARGS+=("--no-allow-unauthenticated")
fi

gcloud run deploy "${DEPLOY_ARGS[@]}"

echo "==> Deployment completed successfully!"
echo "URL Access:"
gcloud run services describe "${SERVICE_NAME}" --region="${REGION}" --format='value(status.url)'
