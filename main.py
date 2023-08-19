#!/usr/bin/env python3
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

# Create an instance of the LLM class using the model directory
llm = LLM(MODEL_DIR)

@app.post("/generate")
async def generate(request: Request) -> Response:
    body = await request.body()
    print("Request Body:", body.decode())  # Print the request body

    try:
        request_dict = await request.json()
    except json.JSONDecodeError:
        return JSONResponse({"error": "Malformed JSON"}, status_code=400)

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
