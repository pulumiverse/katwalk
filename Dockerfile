# Usage:
# ~$ docker build -t ghcr.io/usrbinkat/vllm -f Dockerfile .
# ~$ docker run -it --rm --shm-size=10.24gb -p 8000:8000 --gpus '"device=0,1,2,3"' --hostname cuda --name cuda -v $(pwd)/main.py:/root/test.py -v $HOME/Wizard-Vicuna-13B-Uncensored-HF:/models ghcr.io/usrbinkat/vllm
# ~$ docker run -it --rm --shm-size=10.24gb -p 8000:8000 --gpus '"device=0,1,2,3"' --hostname cuda --name cuda -v $(pwd)/main.py:/root/test.py -v $HOME/Wizard-Vicuna-13B-Uncensored-HF:/models --entrypoint bash ghcr.io/usrbinkat/vllm

# Use Ubuntu 22.04 as the builder image
FROM docker.io/nvidia/cuda:11.8.0-devel-ubuntu22.04

# Apt Packages List
ARG APT_PKGS="\
python3-pip \
python3-dev \
python3-full \
"

# Environment
ENV CUDA_HOME="/usr/local/cuda-11.8"
WORKDIR /app

# reduce optional and suggested package installs
COPY apt.conf /rootfs/etc/apt/apt.conf.d/apt.conf
COPY main.py /app/main.py

# Update packages
RUN set -ex \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ${APT_PKGS} \
    && apt-get clean \
    && apt-get autoremove -y \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/* \
    && echo


# Python Packages List
ARG PIP_PKGS="\
ray \
vllm \
huggingface_hub \
"

# Install pip packages
RUN set -ex \
    && cd /root \
    && python3 --version \
    && python3 -m pip install ${PIP_PKGS} \
    && rm -rf /root/.cache \
    && echo

# Set the default command
CMD ["python3", "/app/main.py"]

LABEL org.opencontainers.image.source=https://github.com/usrbinkat/katwalk
LABEL org.opencontainers.image.description="KatWalk Server - Distributed LLM API Runtime Container"
LABEL org.opencontainers.image.licenses=APACHE2