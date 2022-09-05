# Build and run the image locally
# To use GCP Firestore, you need to have the credentials JSON file in $(pwd)/../firestore-credentials.json

docker build . -t kickup:latest
echo "================================"
echo "========BUILD COMPLETE=========="
echo "================================"

docker run --rm -it \
  -e GOOGLE_APPLICATION_CREDENTIALS=/firestore-credentials.json \
  -v $(pwd)/../firestore-credentials.json:/app/firestore-credentials.json \
  -e PORT=5000 \
  -p 5000:5000 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/firestore-credentials.json \
  kickup:latest

