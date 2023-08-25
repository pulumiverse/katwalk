from pulumi import Input, Output
from pulumi.dynamic import Resource, ResourceProvider, CreateResult, UpdateResult
from typing import Optional
import runpod

# Very Insecure!!!!
runpod.api_key = ""

class RunPodArgs(object):

    name: Input[str]
    image: Input[str]
    gpu_type: Input[str]

    def __init__(self, name, image, gpu_type):
        self.name = name
        self.image = image
        self.gpu_type = gpu_type

class RunPodProvider(ResourceProvider):

    def create(self, props):
        p = runpod.create_pod(
            name=props["name"],
            image_name=props["image"],
            gpu_type_id=props["gpu_type"])
        print(p)
        return CreateResult(p['id'], {**props, **p})

    def delete(self, id, props):
        runpod.terminate_pod(id)

class RunPod(Resource):

    name: Output[str]
    image: Output[str]
    gpu_type: Output[str]
    id: Output[str]

    def __init__(self, name, args: RunPodArgs, opts = None):
        full_args = {'name':None, 'image':None, 'gpu_type':None, **vars(args)}
        super().__init__(RunPodProvider(), name, full_args, opts)

# containerDiskInGb, dockerArgs, env, imageName, name, and volumeInGb