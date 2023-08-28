"""A Python Pulumi program"""
"""
This program optionally:
 - Builds katwalk server container
 - Deploys to Locally via Docker
 - Deploys in the cloud to:
   - Azure Container Instances (ACI)
   - Runpod.io
"""

import os
import sys

# Import Pulumi libraries
import pulumi
from pulumi import Output

# Add parent directory to sys.path to import local modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Import local runpod dynamic provider module
from runpod_provider.pod import create_pod

# Import local libraries
from azure_aci import azure_aci
from docker_run import docker_run
from image_build import docker_build

# Initialize empty variables
models_path = None
registry_password = None

# Load config settings from `pulumi config set` user commands
config = pulumi.Config()

# Service Deployment Configuration
deploy_service = config.get_bool("deploy") or False
container_runtime = config.get("runtime") or None

if deploy_service == True:
    # HuggingFace Settings
    hf_repo = config.get("hfModel")
    hf_username = config.require("hfUsername")
    hf_token = config.require_secret("hfToken")
    # Incomplete feature to allow multiple models to be downloaded
    hf_repo_download_list = config.get("hfModelDownloadList") or hf_repo

# IaC Configuration
build_image = config.get_bool("buildImage") or False
if build_image:
    image_skip_push = config.get_bool("skipImageUpload") or False # False = Do push image to registry
else:
    print("Config 'build_image=False' skipping task docker_build...")

# Image name / Registry Credentials
# Used for optional pull and push
image_tag = config.get("imageTag") or "latest"
image_name = config.get("imageName") or "katwalk"
registry_server = config.get("registry") or "ghcr.io"
registry_username = config.get("username") or "usrbinkat"
registry_namespace = config.get("registryNamespace") or registry_username
image_name_full = f"{registry_server}/{registry_namespace}/{image_name}:{image_tag}"

# Check if image build is enabled, and if push is enabled,
# and if so load the password from config or abort if not found
if build_image and not image_skip_push:
    registry_password = config.require_secret("password")

# If build_image is enabled, build the image and cache locally,
# also push to registry if push is enabled
if build_image:
    print("building image")
    image_platform = "linux/amd64"
    dockerfile_path = "./Dockerfile"
    docker_build_context = "."
    image = docker_build(
        image_platform,
        image_name_full,
        image_skip_push,
        registry_server,
        registry_username,
        registry_password,
        docker_build_context
    )

# Deploy Service if enabled
# Determine container runtime and run the container
# Fallback to running locally on docker if not specified
if deploy_service and container_runtime == "docker" or container_runtime == None:
    print("Deploying container locally with Docker...")

    # Set models_path to user provided path
    # else if None, default provision/use local docker volume
    models_path = config.get("modelsPath")
    
    # Run the container
    container_id = docker_run(
        hf_username,
        hf_repo,
        hf_token,
        image_name,
        image_name_full,
        models_path
    )

if deploy_service and container_runtime == "azure":
    print("Running container in the cloud with Azure Container Instances...")
    
    # Deploy the container to Azure Container Instances
    container_name = azure_aci(
        username=hf_username,
        model=hf_repo,
        hf_token=hf_token,
        image_name=image_name,
        image_name_full=image_name_full,
        password=registry_password,
        location="eastus",
        resource_group_name=image_name
    )

# Check if the container runtime is set to "runpod" and if the deploy_service flag is True
if container_runtime == "runpod" and deploy_service == True:
    print("Generating Runpod.io Deployment ...")

    # Runpod.io Settings
    rp_token = config.require_secret("runpodToken") # Get Runpod token as a secret
    rp_token_str = Output.from_input(rp_token).apply(lambda token: f"{token}") # Convert the secret to a string (idk why this is needed but it is)
    
    # Specify the type of GPU to use
    gpu = config.get("runpodGpu") or "NVIDIA RTX A6000"
    
    # Set the API key for Runpod.io
    rp_token_str = Output.from_input(rp_token).apply(lambda token: f"{token}")
    
    # Define environment variables for the container
    env = {
        # HuggingFace Credentials
        "HF_TOKEN": hf_token,
        "HF_USER": hf_username,
        # HuggingFace Model
        "HF_REPO": hf_repo
    }
    
    # Define volume mounts for the container
    mounts = "/models"
    
    # Define ports to publish from the container
    # comma separated list of ports
    # valid format - "8888/http,666/tcp"
    ports = "8000/http" 
    
    # Set the disk size for the volume in GB
    volume_disk = "80"
    
    # Set the disk size for the container in GB
    container_disk = "16"
    
    # Specify the number of GPUs to allocate
    gpu_count = "1"
    
    # Specify the type of cloud to deploy on
    cloud_type = "secure cloud"
    
    # Call the 'create_pod' function from the 'rp' module to create the container
    # Store the returned container ID
    container_id = create_pod(
        name=image_name,
        image_name=image_name_full,
        api_key=rp_token_str,
        gpu=gpu,
        gpu_count=gpu_count,
        container_disk=container_disk,
        volume_disk=volume_disk,
        mounts=mounts,
        ports=ports,
        env=env,
        cloud_type=cloud_type
    )
    
    # Export the container ID using Pulumi's export function
    pulumi.export("container_id", container_id.container_id)

# If deploy_service is enabled, and container_runtime is not specified,
# or if container_runtime is specified but not supported, throw an error
if deploy_service == True and container_runtime not in [None, 'docker', 'azure', 'runpod']:
    raise ValueError(f"\n\nContainer runtime '{container_runtime}' is not supported.\nPlease set 'runtime' to 'docker', 'azure', or 'runpod'.\n")

# Stack exports
pulumi.export("containerBuildImage", image_name_full)
pulumi.export("containerRuntime", container_runtime)
