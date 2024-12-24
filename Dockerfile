# Use the Python 3.9 image based on Alpine Linux (lightweight and small).
FROM python:3.9-alpine3.13

# Add metadata about the image creator.
LABEL maintainer="tunisiaappdeveloper.tn"

# Set an environment variable to disable Python output buffering.
ENV PYTHONUNBUFFERED 1

# Copy the requirements files into the container.
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy the application code into the container.
COPY ./app /app

# Set /app as the working directory inside the container.
WORKDIR /app

# Expose port 8000 for the Django application.
EXPOSE 8000

# Define a build argument for development mode.
ARG DEV=false

# Install system dependencies and Python packages.
RUN apk update && \
    apk add --no-cache \
        postgresql-client \
        build-base \
        postgresql-dev \
        musl-dev && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp

# Update the PATH environment variable to include the virtual environment binaries.
ENV PATH="/py/bin:$PATH"

# Create a non-root user and switch to it for better security.
RUN adduser \
    --disabled-password \
    --no-create-home \
    django-user
USER django-user
