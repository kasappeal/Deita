FROM python:3.12-slim

WORKDIR /workspace

RUN apt-get update                                                          && \
    apt-get install -y build-essential curl git wget unzip sudo             && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | sudo bash -          && \
    apt-get install -y nodejs                                               && \
    npm --version                                                           && \
    node --version                                                          && \
    pip install --no-cache-dir uv                                           && \
    groupadd --gid 1000 app                                                 && \
    useradd --uid 1000 --gid app --shell /bin/bash --create-home app        && \
    echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/app                 && \
    chmod 0440 /etc/sudoers.d/app                                           && \
    mkdir -p /workspace/data                                                && \
    chown -R app:app /workspace

# Switch to app user
USER app

# Set environment variables
ENV PATH="/home/app/.local/bin:$PATH"
# ENV PYTHONPATH="/workspace/backend"

# Default command
CMD ["sleep", "infinity"]
