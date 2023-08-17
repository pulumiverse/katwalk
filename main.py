#!/usr/bin/env python3
import argparse
import json
import torch
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from vllm import LLM, SamplingParams


MODEL_DIR = "/models"
app = FastAPI()

# Create an instance of the LLM class using the model directory and tensor_parallel_size
tensor_parallel_size = torch.cuda.device_count() if torch.cuda.device_count() > 1 else 1
llm = LLM(MODEL_DIR, tensor_parallel_size=tensor_parallel_size)

# If multiple GPUs are available, wrap the LLM instance with DataParallel
if torch.cuda.device_count() > 1:
    print(f"Using {torch.cuda.device_count()} GPUs")
    llm = torch.nn.DataParallel(llm)

@app.post("/generate")
async def generate(request: Request) -> Response:
    request_dict = await request.json()
    prompt = request_dict.pop("prompt")
    sampling_params = SamplingParams(**request_dict)

    # Generate the results using the LLM instance
    result = llm.generate([prompt], sampling_params)  # Pass prompt as a list

    # Extract the text from the result
    text_outputs = [output.text for output in result[0].outputs]

    ret = {"text": text_outputs}
    return JSONResponse(ret)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level="debug")
