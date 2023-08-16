# Usage:
# ~$ docker build -t docker.io/library/test:test -f Dockerfile .
# ~$ docker run -it --rm docker.io/library/test:test

# Use Ubuntu 23.04 Lunar Lobster as the builder image
FROM ubuntu:lunar AS builder

# Set the chroot build path
ARG BUILD_PATH='/rootfs'

# Set chroot build release Ubuntu 23.04 Lunar Lobster
ARG RELEASE='lunar'

# Chroot Apt Packages Include
ARG BOOTSTRAP_PKGS="\
vim \
"

# Apt Packages List
ARG APT_PKGS="\
python3-full \
python3-pip \
"

# Install debootstrap and create a minimal Ubuntu filesystem
RUN set -ex \
    && mkdir -p ${BUILD_PATH} \
    && apt-get update \
    && apt-get install -y --no-install-recommends debootstrap \
    && debootstrap \
           --variant=minbase \
           --include="${BOOTSTRAP_PKGS}" \
           ${RELEASE} ${BUILD_PATH} \
    && cat /etc/apt/sources.list > ${BUILD_PATH}/etc/apt/sources.list \
    && echo

COPY apt.conf /rootfs/etc/apt/apt.conf.d/apt.conf

# Update packages in the chroot
RUN set -ex \
    && chroot ${BUILD_PATH} apt-get update \
    && chroot ${BUILD_PATH} apt-get upgrade -y \
    && chroot ${BUILD_PATH} apt-get clean \
    && chroot ${BUILD_PATH} apt-get purge -y --auto-remove \
    && rm -rf ${BUILD_PATH}/var/lib/apt/lists/* \
    && echo

# Install python inside the chroot environment
RUN set -ex \
    && chroot ${BUILD_PATH} apt-get update \
    && chroot ${BUILD_PATH} apt-get install -y --no-install-recommends ${APT_PKGS} \
    && chroot ${BUILD_PATH} apt-get clean \
    && chroot ${BUILD_PATH} apt-get autoremove -y \
    && chroot ${BUILD_PATH} apt-get purge -y --auto-remove \
    && rm -rf ${BUILD_PATH}/var/lib/apt/lists/* \
    && echo

# Build from scratch using rootfs chroot from builder
FROM scratch

# Python Packages List
ARG PIP_PKGS="\
huggingface_hub \
"

# Permanent VENV
WORKDIR /root

# Copy the minimal Ubuntu filesystem from the builder image
COPY --from=builder /rootfs /

# Install pip packages
ENV VIRTUAL_ENV="/opt/venv"
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN set -ex \
    && cd /root \
    && python3 --version \
    && python3 -m venv ${VIRTUAL_ENV} \
    && python3 -m pip install ${PIP_PKGS} \
    && echo

RUN set -ex \
    && apt update \
    && apt install gnupg2 -y \
    && apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/3bf863cc.pub \
    && apt update \
    && echo

ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
ENV NVIDIA_REQUIRE_CUDA "cuda>=8.0"

RUN set -ex \
    && echo "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2304/$(uname -m) /" > /etc/apt/sources.list.d/cuda.list \
    && echo

# Set the default command
CMD ["/bin/bash"]
