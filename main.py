#!/usr/bin/env python3
# Import necessary libraries
import os
from vllm import VLLMModel

# Get the base model directory from the environment variable
MODEL_DIR = os.environ.get('MODEL_DIR', '/models')  # Default to '/models' if not set

# Define the models to be served
models = [
    VLLMModel(name="LLaMA-2-7b-hf", path=os.path.join(MODEL_DIR, "path/to/model1")),
    VLLMModel(name="GPT-2", path=os.path.join(MODEL_DIR, "path/to/model2")),
    # Add more models as needed, using os.path.join(MODEL_DIR, "path/to/model")
]