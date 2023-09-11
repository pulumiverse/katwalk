"""A Python Pulumi program"""
"""
This program optionally:
 - Builds katwalk server container
 - Deploys Locally via Docker
 - Deploys in the cloud to:
   - Runpod.io
   - Azure Container Instances (ACI)
"""

import os
import sys

# Import Pulumi libraries
import pulumi
import pulumiverse_vercel as vercel
from pulumi import Output

# Add parent directory to sys.path to import local modules
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

# Import local runpod dynamic provider module
from runpod_provider.pod import create_pod

# Import local docker modules
from docker_provider.run import docker_run
from docker_provider.build import docker_build

# Import local libraries
from azure_provider.aci import azure_aci

# Initialize empty variables
config_oci_secret = None
config_docker_hostdir = None

# Load config settings from `pulumi config set` user commands
config = pulumi.Config()
project_name = config.get("deploymentName") or "katwalk"
token = config.require_secret("token")
repoName = config.require("repoName")
repoType = config.require("repoType")

# Service Deployment Configuration
config_deploy_service = config.get_bool("deploy") or False # Default: do not deploy service
config_container_runtime = config.get("runtime") or "docker" # Default to docker if not specified

# set huggingface config if config_deploy_service is enabled
if config_deploy_service == True:
    # HuggingFace Settings
    config_hf_model_id = config.get("hfModel") or "meta-llama/Llama-2-7b-chat-hf"
    config_hf_user = config.require("hfUsername")
    config_hf_token = config.require_secret("hfToken")
    # Incomplete feature to allow multiple models to be downloaded
    config_hf_model_id_download_list = config.get("hfModelDownloadList") or config_hf_model_id

# Docker Image Name & Container Registry Credentials
# Used for optional pull and push
config_docker_tag = config.get("dockerTag") or "latest"
config_docker_name = config.get("dockerName") or "katwalk"
config_oci_user = config.get("dockerUser") or "usrbinkat"
config_oci_server = config.get("dockerRegistry") or "ghcr.io"
config_oci_project = config.get("dockerProject") or config_oci_user
config_docker_name_full = f"{config_oci_server}/{config_oci_project}/{config_docker_name}:{config_docker_tag}"
config_docker_build = config.get_bool("dockerBuild") or False # Default: do not build image

# Secret is only required for deploying if target is azure
if config_deploy_service and config_container_runtime == "azure":
    config_oci_secret = config.require_secret("dockerRegistrySecret")


#############################################################
# Build Image if enabled
#############################################################

# If build_image is enabled, build the image and cache locally,
# also push to registry if push is enabled
if config_docker_build:
    print(f"[config_docker_build=True] Building image {config_docker_name_full}...")

    # Check if docker image should be pushed to registry
    config_docker_push = config.get_bool("dockerPush")
    if config_docker_push:
        print(f"Config 'dockerPush=True' enabling task pushing image to registry {config_docker_name_full}...")
        # Require secret for pushing to registry
        config_oci_secret = config.require_secret("dockerRegistrySecret")
        # False = Do push image to registry, it's confusing and weird like me :/
        docker_image_skip_push = False
    else:
        print(f"Config 'dockerPush=False' skipping task pushing image to registry {config_docker_name_full}...")
        # True = Do not push image to registry (because that makes sense or some shit)
        # It's not my fault I swear
        docker_image_skip_push = True

    # Docker Build Arguments
    docker_image_arch = "linux/amd64"
    docker_dockerfile_path = "../docker/Dockerfile"
    docker_build_context = "../"

    # Build the image
    image = docker_build(
        docker_image_arch,
        config_docker_name_full,
        docker_image_skip_push,
        config_oci_server,
        config_oci_user,
        config_oci_secret,
        docker_build_context,
        docker_dockerfile_path
    )

    # export container image name
    pulumi.export("containerBuildImage", config_docker_name_full)


#############################################################
# Deploy Service if enabled
# Determine container runtime and run the container
#############################################################

# Docker
# Runtime=docker platform
if config_deploy_service and config_container_runtime == "docker":
    print("Generating Local Docker Deployment ...")

    # Set config_docker_hostdir to user provided path
    # else if None, default provision/use local docker volume
    config_docker_hostdir = config.get("modelsPath")

    # Run the container
    container_id = docker_run(
        project_name,
        config_hf_user,
        config_hf_token,
        config_hf_model_id,
        config_docker_name_full,
        config_docker_hostdir
    )


# Azure
# Runtime=azure platform
if config_deploy_service and config_container_runtime == "azure":
    print("Generating Azure ACI Deployment ...")

    # Load GPU settings from Pulumi config or default to 1 x V100
    config_azure_aci_gpu = config.get("azureAciGpu") or "V100"
    config_azure_aci_gpu_count = config.get_int("azureAciGpuCount") or 1

    # Azure Region
    region="eastus"

    print(f"Deploying {project_name} container in the cloud with Azure ...")
    # Deploy the container to Azure Container Instances
    container_name = azure_aci(
        project_name,
        config_hf_user,
        config_hf_token,
        config_hf_model_id,
        config_azure_aci_gpu,
        config_azure_aci_gpu_count,
        config_docker_name_full,
        config_oci_project,
        config_oci_secret,
        config_oci_server,
        region
    )


# Runpod.io
# runtime=runpod platform
if config_deploy_service and config_container_runtime == "runpod":
    print("Generating Runpod.io Deployment ...")

    # Define a function to format the URL
    def format_url(id):
        return f"https://{id}-8000.proxy.runpod.net/v1/chat"

    # Require Runpod.io Token if deploy_service=True
    config_rp_token = config.require_secret("runpodToken") # Get Runpod token as a secret

    config_rp_gpu_type = config.get("runpodGpuType") or "NVIDIA RTX A6000" # Specify the type of GPU to use
    config_rp_gpu_count = str(config.get("runpodGpuCount")) or "1" # Specify the number of GPUs to allocate

    # Specify the type of cloud to deploy on
    config_rp_cloud_type = "secure cloud"

    # Set container and volume disk size for the volume in GB
    config_rp_container_disk_size_gb = "16"
    config_rp_volume_disk_size_gb = "80"

    # Define environment variables for the container
    env = {
        # HuggingFace Credentials
        "HF_USER": config_hf_user,
        "HF_TOKEN": config_hf_token,
        # HuggingFace Model ID
        "HF_REPO": config_hf_model_id,
        "REFRESH_REPOSITORIES": "True"
    }

    mounts="/models"
    ports="8000/http" # valid format - "8888/http,666/tcp"
    env=env

    # Call the 'create_pod' function from the 'rp' module to create the container
    # Store the returned container ID
    container_id = create_pod(
        project_name,
        config_docker_name_full,
        config_rp_token,
        config_rp_gpu_type,
        config_rp_gpu_count,
        config_rp_container_disk_size_gb,
        config_rp_volume_disk_size_gb,
        config_rp_cloud_type,
        mounts,
        ports,
        env
    )

    # Export the container ID using Pulumi's export function
    runpod_id_fqdn = container_id.id.apply(format_url)
    pulumi.export("container_id", container_id.id)
    pulumi.export("ChatbotURL", runpod_id_fqdn)

#############################################################
# Error Handling
#############################################################

# If config_deploy_service is enabled, and config_container_runtime is not specified,
# or if config_container_runtime is specified but not supported, throw an error
if config_deploy_service and config_container_runtime not in ['docker', 'azure', 'runpod']:
    raise ValueError(f"\n\nContainer runtime '{config_container_runtime}' is not supported.\nPlease set 'runtime' to 'docker', 'azure', or 'runpod'.\n")


#############################################################
# FRONTEND INFRASTRUCTURE
#############################################################

provider = vercel.Provider("vercel-provider",
    api_token = token
)

project = vercel.Project("vercel-project", 
    name = "vercel-git-project",
    framework = "vue",
    git_repository = vercel.ProjectGitRepositoryArgs(
        repo = repoName,
        type = repoType
    ),
    opts = pulumi.ResourceOptions(
        provider = provider
    )
)

environment = vercel.ProjectEnvironmentVariable("vercel-env",
    project_id = project.id,
    key = "VUE_APP_BACKEND_DNS",
    value = runpod_id_fqdn,
    targets = ["production"],
    opts = pulumi.ResourceOptions(
        provider = provider
    )
)

deployment = vercel.Deployment("vercel-deployment",
    project_id = project.id,
    production = True,
    ref = "main",
    opts = pulumi.ResourceOptions(
        provider = provider
    )
)