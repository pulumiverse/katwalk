# Description: This file contains the code to run a Docker container locally.
# https://www.pulumi.com/registry/packages/docker/api-docs/container/
from pulumi import Output
from pulumi_docker import Container, ContainerPortArgs, ContainerMountArgs, Volume

# Run a Docker container locally
def docker_run(username, model, hf_token, image_name, image_name_full, models_path):

    # Extract the string value of hf_token
    hf_token_str = Output.from_input(hf_token).apply(lambda token: f"{token}")

    # Determine mount_type and create a Docker volume if a path is not provided
    if models_path is None:
        mount_type = "volume"
        models_volume = Volume("katwalk-model-volume")
        models_path = models_volume.name
    else:
        mount_type = "bind"

    # Create a container, configure it, and run the image locally
    container = Container(image_name,
        image=image_name_full,
        ports=[ContainerPortArgs(internal=8000, external=8000)],  # Expose port 8000
        envs=[
            "REFRESH_REPOSITORIES=True",
            f"HF_USER={username}",
            f"HF_REPO={model}",
            f"HF_TOKEN={hf_token_str}",
        ],  # Set environment variables
        gpus="all",  # Equivalent of --gpus=all
        mounts=[
            # Mount a local directory or volume for model storage
            ContainerMountArgs(
                target="/models",
                source=models_path,
                type=mount_type
            )
        ],
        command=["python", "main.py"],
        attach=False,
        hostname="katwalk",  # Set hostname of container
        shm_size=10 * 1024 * 1024 * 1024  # Convert GBs to Bytes and set shared memory size
    )

    # Stack exports
    return container.id
