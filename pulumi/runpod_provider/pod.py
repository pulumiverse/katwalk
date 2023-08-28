# Import the 'runpod-python' library
import runpod
# Import the RunPod, RunPodArgs, and RunPodProvider classes from the local '.provider' module
from .provider import RunPod, RunPodArgs

# Define a function called 'create_pod' that takes multiple arguments
def create_pod(
        name,  # Name of the pod
        image_name,  # Name of the image to use
        gpu,  # GPU type
        api_key,  # API key for authentication
        env,  # Environment variables
        mounts,  # Mount points for volumes
        ports,  # Ports to publish
        volume_disk,  # Disk size for the volume
        container_disk,  # Disk size for the container
        cloud_type,  # Type of cloud to deploy on
        gpu_count  # Number of GPUs to allocate
    ):
    print("Deploying container in the cloud with Runpod.io...")

    # Set the API key for the 'runpod' module
    runpod.api_key = api_key
    
    # Create a new RunPod object and return it
    # The RunPod object is initialized with the 'name' and a RunPodArgs object
    # The RunPodArgs object is initialized with all the function arguments
    return RunPod(
        name, 
        RunPodArgs(
            name=name, 
            image_name=image_name, 
            api_key=api_key,
            gpu=gpu,
            #gpu_count=gpu_count
            container_disk=container_disk,
            volume_disk=volume_disk,
            mounts=mounts,
            ports=ports,
            env=env,
            #cloud_type=cloud_type,
        )
    )
