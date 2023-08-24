# Description: This file contains the function to build a docker image
# and push it to a registry.
# https://www.pulumi.com/registry/packages/docker/api-docs/image/
from pulumi_docker import Image

def docker_build(
    image_platform,
    image_name_full,
    image_skip_push,
    registry_server,
    registry_username,
    registry_password,
    docker_build_context):

    print(f"Building image: {image_name_full}...")

    image = Image(image_name_full,
        image_name=image_name_full,
        build={
            "context": docker_build_context,
            "platform": image_platform
        },
        skip_push=image_skip_push,
        registry={
            "server": registry_server,
            "username": registry_username,
            "password": registry_password
        }
    )
