# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
ENV MOD_HOME $APP_HOME/kickup
WORKDIR $APP_HOME
COPY . ./
WORKDIR $MOD_HOME
# Install production dependencies.
RUN pip install --no-cache-dir -r $APP_HOME/requirements.txt

# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 kickup:app