#gcloud artifacts repositories create kickup-repo --repository-format=docker --location=europe-west6 --description="Docker repository for kickup images"

PROJECT_ID=$(gcloud config get-value project)
echo $PROJECT_ID
gcloud builds submit --region=europe-west1 --tag  "europe-west6-docker.pkg.dev/$PROJECT_ID/kickup-repo/kickup:latest"
