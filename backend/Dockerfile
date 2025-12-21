# Use Ubuntu 22.04 as base OS
FROM ubuntu:22.04

# Set non-interactive mode for apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Set the working directory
WORKDIR /app

# Install system dependencies and Python 3.11
RUN apt-get update && apt-get install -y \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using specific python version
# We create a venv to follow best practices on Ubuntu
RUN python3.11 -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy requirements AFTER heavy installs to avoid cache invalidation on req changes
COPY requirements.txt /app/

# Install remaining dependencies
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# Install large ML dependencies first (CPU versions) to save time and space
# We use a cache mount to persist the pip cache between builds
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install sentence-transformers transformers

RUN python -c "import pypandoc; pypandoc.download_pandoc()"


# Copy source code
COPY . /app

EXPOSE 8000

# Default to running the gateway if no command is specified in docker-compose
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]