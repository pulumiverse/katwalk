"""A Python Pulumi program"""

import pulumi
import pulumi
from pulumi_docker import Image, Container, ContainerPortArgs, ContainerMountArgs

# Build docker image using a local Dockerfile.
image = Image(
    "ghcr.io/usrbinkat/vllm:latest",
    build = {
        "context": ".",
        "platform": "linux/amd64"
    },
    image_name="ghcr.io/usrbinkat/vllm:latest",
    skip_push=True
)
pulumi.export(
    "ghcr.io/usrbinkat/vllm:latest",
    image.image_name
)

# Create a container, configure it and run the image locally.
container = Container(
    "cuda",
    image=image.base_image_name,
    ports=[ContainerPortArgs(internal=8000,external=8000)],  # expose port 8000
    envs=["HF_USER=usrbinkat"],  # set environment variable
    gpus="all", # equivalent of --gpus=all
    mounts=[
        # Mount a local directory. Let's assume we will 'bind' the source to target.
        ContainerMountArgs(target="/models", source="/home/kat/models", type="bind")
    ],
    command=["sleep", "infinity"],
    attach="false",
    hostname="cuda",  # set hostname of container
    shm_size=10*1024*1024*1024  # convert GBs to Bytes and set Shared memory size
)

# Stack exports
pulumi.export("imageName", image.image_name)
pulumi.export("containerId", container.id)
