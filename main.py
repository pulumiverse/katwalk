#!/usr/bin/env python3
# Import necessary libraries
import os
from vllm import VLLMModel
from vllm import VLLMServer

# Get the base model directory from the environment variable
MODEL_DIR = os.environ.get('MODEL_DIR', '/models')  # Default to '/models' if not set

# Define the models to be served
models = [
    VLLMModel(name="LLaMA-2-7b-hf", path=os.path.join(MODEL_DIR, "llama-2-7b-hf")),
#   VLLMModel(name="LLaMA-2-13b-hf", path=os.path.join(MODEL_DIR, "llama-2-13b-hf")),
]

# Configure the vLLM server
server = VLLMServer(models=models, port=8000, workers=4)

# Define API endpoints
def inference(request):
    model_name = request.get("model_name")
    input_text = request.get("input_text")
    model = server.get_model(model_name)
    output = model.infer(input_text)
    return {"output": output}

def status(request):
    return {"status": "OK"}

# start the server
if __name__ == "__main__":
    server.start()