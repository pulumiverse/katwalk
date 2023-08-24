"""A Python Pulumi program"""

# Import Pulumi libraries
import pulumi
from azure_aci import azure_aci


# Import local libraries
from image_build import docker_build
from docker_run import docker_run

# `None` variable defaults
models_path = None
registry_password = None

# Load config settings from `pulumi config set` user commands
config = pulumi.Config()

# HuggingFace Settings
hf_token = config.get_secret("hfToken")
hf_username = config.require("hfUsername")
hf_repo = config.get("hfModel")
hf_repo_download_list = config.get("hfModelDownloadList") or hf_repo

# Service Deployment Configuration
deploy_service = config.get_bool("deploy") or False
container_runtime = config.get("runtime") or None

# IaC Configuration
build_image = config.get_bool("buildImage") or False # Default to False, but allow override in Pulumi config
image_skip_push = config.get_bool("skipImageUpload") or False # False = Do push image to registry

# Registry Credentials
# Used for pull and optionally push
registry_server = config.get("registry") or "ghcr.io"
registry_username = config.get("username") or "usrbinkat"
registry_namespace = config.get("registryNamespace") or registry_username

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
    
    # Set models_path to user provided path
    # else if None, will default to create and use a docker volume
    models_path = config.get("modelsPath")
    
    # Define the resource group name (if needed)
    resource_group_name = "myResourceGroup"

    # Call the azure_aci function
    container_name = azure_aci(
        username=hf_username,
        model=hf_repo,
        download_list=hf_repo_download_list,
        hf_token=hf_token,
        image_name=image_name,
        image_name_full=image_name_full,
        password=registry_password,
        location="East US", # You can customize the location if needed
        resource_group_name=resource_group_name
    )


elif deploy_service == True and container_runtime != None and container_runtime != "docker" and container_runtime != "azure":
    raise ValueError(f"\n\nContainer runtime '{container_runtime}' is not supported.\nPlease set 'runtime' to 'docker' or 'azure'.\n")

# Stack exports
pulumi.export("containerBuildImage", image_name_full)