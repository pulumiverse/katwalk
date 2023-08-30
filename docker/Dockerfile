# Example Usage:
# 
# Build
# ~$ docker build -f docker/Dockerfile -t ghcr.io/usrbinkat/katwalk .
# 
# Develop
# ~$ docker run -it --rm --shm-size=10.24gb -p 8000:8000 --gpus=all -v $HOME/models:/models --entrypoint bash ghcr.io/usrbinkat/katwalk
# 
# Run
# ~$ docker run -it --rm --shm-size=10.24gb -p 8000:8000 --gpus '"device=0"' -e HF_USER=usrbinkat -e HF_REPO="meta-llama/Llama-2-7b-chat-hf" -e HF_REPOS="meta-llama/Llama-2-7b-chat-hf" -e HF_TOKEN="hf_TKZXXXXXXXXXXXXXXXURSfd" -v $HOME/models:/models ghcr.io/usrbinkat/katwalk

# Use Ubuntu 22.04 as the builder image
FROM docker.io/nvidia/cuda:11.8.0-devel-ubuntu22.04

# Set cuda path
ENV CUDA_HOME="/usr/local/cuda-11.8"

# Apt Flags & Package List
ARG APT_PKGS="\
git \
git-lfs \
python3-pip \
python3-dev \
python3-full \
"

# Append rootfs directory tree into container
# place any additional files to be included into the rootfs directory
ADD docker/rootfs /

# Disable Timezone prompts
ENV TZ=UTC
# Disable time zone prompts etc.
ARG DEBIAN_FRONTEND=noninteractive
# Install apt packages
RUN set -ex \
    && apt-get update \
    && apt-get install ${APT_PKGS} \
    && update-alternatives --install \
        /usr/bin/python \
        python \
        /usr/bin/python3 1 \
    && apt-get clean \
    && apt-get autoremove -y \
    && apt-get purge -y --auto-remove \
    && rm -rf \
        /var/lib/{apt,dpkg,cache,log} \
        /usr/share/{doc,man,locale} \
        /var/cache/apt \
        /root/.cache \
        /var/tmp/* \
        /tmp/* \
    && true

# Install Python package vllm as it's own layer
RUN set -ex \
    && python --version \
    && python -m pip install --no-cache-dir git+https://github.com/chu-tianxiang/vllm-gptq@gptq \
    && rm -rf \
        /var/lib/{apt,dpkg,cache,log} \
        /usr/share/{doc,man,locale} \
        /var/cache/apt \
        /root/.cache \
        /var/tmp/* \
        /tmp/* \
    && true

COPY src/app/katwalk/requirements.txt /requirements.txt

# Install Python dependencies from requirements.txt
RUN set -ex \
    && python --version \
    && python -m pip install --no-cache-dir -r /requirements.txt \
    && rm -rf \
        /var/lib/{apt,dpkg,cache,log} \
        /usr/share/{doc,man,locale} \
        /var/cache/apt \
        /root/.cache \
        /var/tmp/* \
        /tmp/* \
    && true

# Append application src tree into container
ADD src /

# Set default working directory
WORKDIR /app/katwalk

# Expose API service listening port
EXPOSE 8000

# Set the default startup command
CMD ["python", "main.py"]

# Metadata
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG VCS_URL
LABEL org.opencontainers.image.source=$VCS_URL \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$VCS_REF \
      org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.licenses="APACHE2" \
      org.opencontainers.image.vendor="Pulumi - DevRel" \
      org.opencontainers.image.title="KatWalk Server - LLM API CUDA Runtime Container" \
      org.opencontainers.image.description="A containerized environment for running KatWalk Server with CUDA support, designed for AI/ML development and deployment" \
      org.opencontainers.image.documentation="https://github.com/usrbinkat/katwalk" \
      org.opencontainers.image.url="https://github.com/usrbinkat/katwalk" \
      org.opencontainers.image.authors="https://github.com/usrbinkat"
