# Usage:
# ~$ docker build -t ghcr.io/usrbinkat/vllm:test -f Dockerfile .
# ~$ docker run -it --rm --entrypoint bash --hostname cuda --name cuda ghcr.io/usrbinkat/vllm:test

# Use Ubuntu 22.04 as the builder image
FROM docker.io/nvidia/cuda:11.8.0-devel-ubuntu22.04

# Apt Packages List
ARG APT_PKGS="\
python3-pip \
python3-dev \
python3-full \
"

# Permanent VENV
WORKDIR /root

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

ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV CUDA_HOME="/usr/local/cuda-11.8"

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
    && python3 -m venv ${VIRTUAL_ENV} \
    && python3 -m pip install ${PIP_PKGS} \
    && echo

# Set the default command
CMD ["/app/main.py"]
