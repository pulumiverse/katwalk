import argparse
import json
import re
import torch
from fastapi import BackgroundTasks, FastAPI, Request, Response
from fastapi.responses import JSONResponse
import uvicorn
from vllm import LLM, SamplingParams

MODEL_DIR = "/model"
app = FastAPI()

# Create an instance of the LLM class using the model directory
llm = LLM(MODEL_DIR)

# System instruction string
SYS_INSTRUCTION = '''You are a helpful assistant.'''

# Template
TEMPLATE = '<s>[INST] <<SYS>> {{ system_prompt }} <</SYS>> {{ user_message }} [/INST]'

def assemble_prompt(user_prompt):
    # Strip unwanted characters
    user_prompt = re.sub(r'[\n\"\']', '', user_prompt).strip()
    
    print("INFO: prompt_log | original_prompt >> " + user_prompt)

    # Replace placeholders in the template with the SYS instruction and user prompt
    final_prompt = TEMPLATE.replace('{{ system_prompt }}', SYS_INSTRUCTION)
    final_prompt = final_prompt.replace('{{ user_message }}', json.dumps(user_prompt))
    
    # Log the assembled prompt
    print("INFO: prompt_log | system_prompt " + final_prompt)
    return final_prompt

@app.post("/v1/chat")
async def generate(request: Request) -> Response:
    body = await request.body()
    print("Request Body:", body.decode())  # Print the request body

    try:
        request_dict = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Malformed JSON"}, status_code=400)

    user_prompt = request_dict.pop("prompt")
    final_prompt = assemble_prompt(user_prompt)
    sampling_params = SamplingParams(**request_dict)

    # Generate the results using the LLM instance
    result = llm.generate([final_prompt], sampling_params)  # Pass prompt as a list

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
