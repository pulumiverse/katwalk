# Description: This file contains the function to build a docker image
# and push it to a registry.
# https://www.pulumi.com/registry/packages/docker/api-docs/image/
from pulumi_docker import Image

def docker_build(
        docker_image_arch,
        config_docker_name_full,
        docker_image_skip_push,
        config_oci_server,
        config_oci_user,
        config_oci_secret,
        docker_build_context,
        docker_dockerfile_path
    ):
    print(f"[./docker/build.py=docker_build] Building image: {config_docker_name_full}...")
    image = Image(config_docker_name_full,
        image_name=config_docker_name_full,
        build={
            "platform": docker_image_arch,
            "context": docker_build_context,
            "dockerfile": docker_dockerfile_path
        },
        skip_push=docker_image_skip_push,
        registry={
            "server": config_oci_server,
            "username": config_oci_user,
            "password": config_oci_secret
        }
    )
    return image
