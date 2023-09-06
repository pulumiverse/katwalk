import os
import argparse
import json
import re
import torch
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from vllm import LLM, SamplingParams
import model_pull

MODEL_DIR = "/models"
app = FastAPI()

# Configure CORS to allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify specific origins if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create an instance of the LLM class using the model directory
# Read environment variables
repo = os.getenv("HF_REPO")
branch = os.getenv("HF_BRANCH", "main")
destination = f"/models/{repo}/{branch}"

# SYS instruction string
SYS_INSTRUCTION = "<s>[INST] <<SYS>> Please provide a meaningful, detailed, and relevant response. <</SYS>>"

# Template
TEMPLATE = SYS_INSTRUCTION + " {{ user_message }} [/INST]"

# LLM Sampling parameters
TOP_P = 0.9
MAX_TOKENS = 600
TEMPERATURE = 0.7

def assemble_prompt(user_prompt):
    # Strip unwanted characters including newlines, double quotes, and single quotes
    user_prompt = re.sub(r'[\n\"\']', '', user_prompt).strip()
    
    # Replace placeholders in the template with the SYS instruction and user prompt
    final_prompt = TEMPLATE.replace('{{ user_message }}', user_prompt)
    
    print("INFO: assembled_prompt >> " + final_prompt)
    return final_prompt

@app.post("/v1/chat")
async def generate(request: Request) -> Response:
    body = await request.body()
    print("Request Body:", body.decode())  # Print the request body

    try:
        request_dict = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Malformed JSON"}, status_code=400)

    user_prompt = request_dict.get("prompt")
    final_prompt = assemble_prompt(user_prompt)

    sampling_params = SamplingParams(temperature=TEMPERATURE, top_p=TOP_P, max_tokens=MAX_TOKENS)

    # Generate the results using the LLM instance
    result = llm.generate([final_prompt], sampling_params)  # Pass prompt as a list

    # Extract the text from the result
    text_outputs = [output.text for output in result[0].outputs]

    ret = {"text": text_outputs}
    return JSONResponse(ret)

if __name__ == "__main__":
    print("INFO: cloning model repositories")
    model_pull.main()
    llm = LLM(destination)

    print("INFO: Starting API Server")
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    uvicorn.run(app, host=args.host, port=args.port, log_level="debug")
