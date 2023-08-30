# Description: This file contains the code to run a Docker container locally.
# https://www.pulumi.com/registry/packages/docker/api-docs/container/
import pulumi
from pulumi import Output, export
from pulumi_docker import Container, ContainerPortArgs, ContainerMountArgs, Volume

config = pulumi.Config()

# Run a Docker container locally
def docker_run(
        project_name,
        config_hf_user,
        config_hf_token,
        config_hf_model_id,
        config_docker_name_full,
        config_docker_hostdir
    ):
    print("[./docker/run.py=docker_run]\nDeploying container locally with Docker ...\nLocal Docker support requires `nvidia-container-toolkit` ...\n  - https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html")

    # bind hostpath to container mount if supplied
    # create a Docker volume if not and bind to container mount
    if config_docker_hostdir is not None:
        # Set container mount arguments to bind mount
        container_mount_args = ContainerMountArgs(
            type="bind",
            target="/models",
            source=config_docker_hostdir
        )
    else:
        # Create a Docker volume
        models_volume = Volume(f"{project_name}-volume")
        # Set container mount arguments
        container_mount_args = ContainerMountArgs(
            type="volume",
            target="/models",
            source=models_volume.name
        )

    # Create a container, and run the service locally
    print("[./docker/run.py=docker_run] Unwrap hfToken secret ...")
    container_name = f"{project_name}-server"
    container = Container(
        container_name,
        name=container_name,
        image=config_docker_name_full,
        ports=[
            ContainerPortArgs(
                internal=8000,
                external=8000
            )
        ],
        envs=[
            "REFRESH_REPOSITORIES=True",
            f"HF_USER={config_hf_user}",
            f"HF_REPO={config_hf_model_id}",
            config_hf_token.apply(lambda token: f"HF_TOKEN={token}")
        ],
        gpus="all",
        mounts=[container_mount_args],
        command=["python", "main.py"],
        hostname=project_name,
        shm_size=10 * 1024 * 1024 * 1024,  # 10GB in Bytes
        attach=False
    )

    # Stack exports
    export('container_id', container.id)
    return container
