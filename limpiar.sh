#!/bin/bash

# Configuración automática del proyecto actual
PROJECT_ID="qwiklabs-gcp-04-b293d7beb72d"
REGION="us-central1" # Cambia esto si usaste otra región

echo "⚠️ Iniciando limpieza total en el proyecto: $PROJECT_ID"

# 1. Eliminar todos los servicios de Cloud Run
echo "🚀 Eliminando servicios de Cloud Run..."
SERVICES=$(gcloud run services list --platform managed --format="value(SERVICE)" --region=$REGION)
for service in $SERVICES; do
    gcloud run services delete $service --region=$REGION --platform managed --quiet
done

# 2. Eliminar repositorios de Artifact Registry (donde están las imágenes Docker)
echo "📦 Eliminando repositorios de Artifact Registry..."
REPOS=$(gcloud artifacts repositories list --format="value(NAME)" --location=$REGION)
for repo in $REPOS; do
    gcloud artifacts repositories delete $repo --location=$REGION --quiet
done

# 3. Eliminar base de datos Firestore (Modo Nativo)
echo "🔥 Eliminando base de datos Firestore (default)..."
# Nota: Este comando está en fase 'alpha' para bases (default)
gcloud alpha firestore databases delete --database="(default)" --quiet 2>/dev/null || echo "Firestore ya estaba vacío o no disponible."

# 4. Eliminar todas las Cuentas de Servicio (excepto las por defecto de Google)
echo "🔑 Eliminando Cuentas de Servicio personalizadas..."
SAs=$(gcloud iam service-accounts list --format="value(email)" --filter="email !~ gserviceaccount.com$")
for sa in $SAs; do
    gcloud iam service-accounts delete $sa --quiet
done

# 5. Limpiar archivos locales en Cloud Shell
echo "📂 Limpiando archivos locales..."
cd ~
rm -rf news_paper-v1/
rm -rf venv/

echo "✅ Limpieza completada. El proyecto $PROJECT_ID está vacío."
