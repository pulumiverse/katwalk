# Import the 'runpod-python' library
import runpod
from pulumi import Output

# Import the RunPod, RunPodArgs, and RunPodProvider classes from the local '.provider' module
from .provider import RunPod, RunPodArgs

# Define a function called 'create_pod' that takes multiple arguments
def create_pod(
        project_name,  # Name of the pod
        config_docker_name_full,  # Name of the image to use
        config_rp_token,  # API key for authentication
        config_rp_gpu_type,  # GPU type
        config_rp_gpu_count,  # Number of GPUs to allocate
        config_rp_container_disk_size_gb,  # Disk size for the container
        config_rp_volume_disk_size_gb,  # Disk size for the volume
        config_rp_cloud_type,  # Type of cloud to deploy on
        mounts,  # Mount points for volumes
        ports,  # Ports to publish
        env  # Environment variables
    ):
    print("Deploying container in the cloud with Runpod.io ...")

    # Authenticate with the API key
    #runpod.api_key = config_rp_token.apply(lambda token: f"{token}")
    config_rp_token.apply(lambda token: setattr(runpod, 'api_key', token))

    # Create a new RunPod object and return it
    # The RunPod object is initialized with the 'name' and a RunPodArgs object
    # The RunPodArgs object is initialized with all the function arguments
    return RunPod(
        project_name,
        RunPodArgs(
            name=project_name,
            image_name=config_docker_name_full,
            api_key=config_rp_token.apply(lambda token: f"{token}"),
            gpu=config_rp_gpu_type,
            #gpu_count=config_rp_gpu_count
            container_disk=config_rp_container_disk_size_gb,
            volume_disk=config_rp_volume_disk_size_gb,
            #cloud_type=config_rp_cloud_type,
            mounts=mounts,
            ports=ports,
            env=env
        )
    )
