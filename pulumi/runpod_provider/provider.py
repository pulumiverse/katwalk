# Import required modules from Pulumi and Python's standard library
from typing import Optional, Dict, List
from pulumi import Input, Output, ResourceOptions
from pulumi.dynamic import Resource, CreateResult, DiffResult, ResourceProvider
import runpod # Import the custom runpod module

# Define a class to hold the arguments for running a pod
class RunPodArgs:
    def __init__(self,
            name: Input[str],
            image_name: Input[str],
            api_key: Input[str],
            gpu: Input[str],
            gpu_count: Input[int] = None,
            container_disk: Input[int] = None,
            volume_disk: Input[int] = None,
            cloud_type: Input[str] = None,
            mounts: Input[List[Dict[str, str]]] = None,
            ports: Input[List[int]] = None,
            env: Input[Dict[str, str]] = None
        ):
        # Initialize all the properties for running a pod
        self.name = name
        self.image_name = image_name
        self.api_key = api_key
        self.gpu = gpu
        self.gpu_count = gpu_count
        self.container_disk = container_disk
        self.volume_disk = volume_disk
        self.cloud_type = cloud_type
        self.mounts = mounts
        self.ports = ports
        self.env = env

# Define the main RunPod class that inherits from Pulumi's Resource class
class RunPod(Resource):
    container_id: Output[str]
    api_key: Output[str]
    
    def __init__(self, name: str, args: RunPodArgs, opts: Optional[ResourceOptions] = None):
        # Initialize the parent class with the RunPodProvider, name, properties, and options
        super().__init__(RunPodProvider(), name, {'container_id': None, 'api_key': args.api_key, **vars(args)}, opts)

# Define the RunPodProvider class that inherits from Pulumi's ResourceProvider class
class RunPodProvider(ResourceProvider):
    # Define the create method to handle pod creation
    def create(self, props):
        print(f"Deploying to Runpod.io with Dynamic Provider ...")

        # Check if 'api_key' is present in properties, raise an error if not
        if 'api_key' not in props:
            raise ValueError("Missing 'api_key'. This field is required.")
        
        # Set the API key for the runpod module
        runpod.api_key = props['api_key']
        
        # Call the create_pod method from the runpod module and store the result
        result = runpod.create_pod(
            name=props['name'],
            image_name=props['image_name'],
            gpu_type_id=props['gpu'],
            cloud_type=props.get('cloud_type', 'ALL'),
            gpu_count=props.get('gpu_count', 1),
            volume_in_gb=props.get('volume_disk', 0),
            container_disk_in_gb=props.get('container_disk', 16),
            ports=props.get('ports'),
            volume_mount_path=props.get('mounts'),
            env=props.get('env')
        )
        
        print(f"Pod created successfully ...")
        
        # Return a CreateResult object with the ID and output properties
        return CreateResult(id_=result['id'], outs={**result, 'api_key': props['api_key']})

    # Define the delete method to handle pod deletion
    def delete(self, id, props):
        print(f"Terminate pod with ID: {id}")
        
        # Check if 'api_key' is present in properties, raise an error if not
        if 'api_key' not in props:
            raise ValueError("Missing 'api_key'. This field is required.")
        
        # Set the API key for the runpod module
        runpod.api_key = props['api_key']
        
        # Initialize an empty list to hold pod IDs
        pod_ids = []
        
        try:
            print(f"Terminating Pod: {id}")
            result = runpod.terminate_pod(id, props) # TODO: Fix pod not deleting
            print(f"Pod terminated successfully: {result}")
        #except runpod.error.QueryError as e:
        #    print(f"GraphQL Query Error: {e}")
        #    raise
        except:
            return
        #try:
        #    print(f"Checking for pod ID {id} ...")
        #    all_pods = runpod.get_pods()
        #    pod_ids = [pod['id'] for pod in all_pods]
        #except runpod.error.QueryError as e:
        #    print(f"GraphQL Query Error: {e}")
        #    raise
        
        ## Terminate the pod if it exists
        #if id in pod_ids:
        #    print(f"Pod ID {id} found...terminating pod..")
        #    runpod.terminate_pod(id)
        #    print(f"Terminated Pod ID: {id}")
        #else:
        #    print(f"Pod ID {id} is already terminated.")
        #    return

    # Define the diff method to determine if there are changes between old and new properties
    def diff(self, id, olds, news):
        print(f"Diff called with olds: {olds}, news: {news}")
        return DiffResult(changes=olds != news)

    # Define the update method to handle pod updates
    def update(self, id, olds, news):
        print(f"Updating pod with ID: {id}")
        
        # Delete the old pod
        self.delete(id, olds)
        
        # Create a new pod with the new properties
        return self.create(news)
