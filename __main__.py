"""A Python Pulumi program"""

# Import Pulumi libraries
import pulumi

# Import local libraries
from image_build import docker_build
from docker_run import docker_run
import runpod_provider

# `None` variable defaults
models_path = None
registry_password = None

# Load config settings from `pulumi config set` user commands
config = pulumi.Config()

# HuggingFace Settings
hf_token = config.get_secret("hfToken")
hf_username = config.require("hfUsername")
hf_repo = config.get("hfModel") or "meta-llama/Llama-2-7b-chat-hf"
hf_repo_download_list = config.get("hfModel") or "meta-llama/Llama-2-7b-chat-hf" # this is a placeholder for an un-finished feature of katwalk server

# Service Deployment Configuration
deploy_service = config.get_bool("deploy") or False
container_runtime = config.get("runtime") or None

# IaC Configuration
build_image = config.get_bool("buildImage") or False # Default to False, but allow override in Pulumi config
image_skip_push = config.get_bool("skipImageUpload") or False # False = Do push image to registry

# Registry Credentials
# Used for pull and optionally push
registry_server = config.get("registry") or "ghcr.io"
registry_username = config.get("username")
registry_namespace = config.get("registryNamespace") or "usrbinkat"

# Check if image build is enabled, and if push is enabled,
# and if so load the password from config or abort if not found
if build_image and not image_skip_push:
    registry_password = config.get_secret("password")
    if registry_password is None:
        raise ValueError("\n\nA registry password is required when 'image_skip_push' is set to False.\nUse the following command to set a token or password:\n\n    pulumi config set --secret password <value>\n")

# Image metadata settings
image_tag = "latest"
image_name = "katwalk"
dockerfile_path = "./Dockerfile"
docker_build_context = "."
image_platform = "linux/amd64"

# Full image name
image_name_full = f"{registry_server}/{registry_namespace}/{image_name}:{image_tag}"

# If build_image is enabled, build the image and cache locally,
# also push to registry if push is enabled
if build_image:
    print("building image")
    image = docker_build(
        image_name,
        image_platform,
        image_name_full,
        image_skip_push,
        registry_server,
        registry_username,
        registry_password,
        docker_build_context
    )
else:
    print("Config 'build_image=False' skipping task docker_build...")

# Deploy Service if enabled
# Determine container runtime and run the container
# Fallback to running locally on docker if not specified
if container_runtime == None or container_runtime == "docker" and deploy_service == True:
    print("Running container locally with Docker...")

    # Set models_path to user provided path
    # else if None, will default to create and use a docker volume
    models_path = config.get("modelsPath")
    
    # Run the container
    username = hf_username
    model = hf_repo
    download_list = hf_repo_download_list
    container_id = docker_run(
        username,
        model,
        download_list,
        hf_token,
        image_name,
        image_name_full,
        models_path
    )

elif container_runtime == "azure" and deploy_service == True:
    print("Running container in the cloud with Azure Container Instances...")

elif container_runtime == "runpod" and deploy_service == True:
    print("Running container in the cloud with Runpod.io...")

    # Run the pod
    container_id = runpod_provider.RunPod(
        "test", 
        runpod_provider.RunPodArgs(
            "test", 
            image_name_full, 
            "NVIDIA GeForce RTX 3070"
        )
    )


elif deploy_service == True and container_runtime != None and container_runtime not in ["docker","azure","runpod"]:
    raise ValueError(f"\n\nContainer runtime '{container_runtime}' is not supported.\nPlease set 'runtime' to 'docker', 'azure' or 'runpod'.\n")

# Stack exports
pulumi.export("containerBuildImage", image_name_full)