# KatWalk Server - An LLM API Service and IaC

## About:

Katwalk is an llm model deployment api server. In this repository you will find all code required to build a containerized LLM API service and deploy locally or in Azure.

## Limitations: 

Currently, katwalk server is a PoC project and is only tested to run `hf` models from huggingface repositories and is only built for linux/amd64 at this time. Encouragement and or PRs for enhancements are welcome!

```bash
# ACTUAL DEMO

kat@cuda:~$ curl -s -X 'POST' 'http://localhost:8000/v1/chat' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"prompt": "Tell me a story about a little robot."}' | jq .
{
  "text": [
    "\nOnce upon a time, there was a little robot named R2. R2 was a friendly and curious robot who lived in a big city. One day, R2 decided to go on an adventure. He set out to explore the city and learn about all the different things he could see and do.\nAs R2 explored the city, he met all kinds of people. Some were kind and welcoming, while others were scared or suspicious of him. Despite this, R2 continued to be friendly and curious, always asking questions and trying to learn more about the world around him.\nOne day, while R2 was exploring a busy market, he saw a group of people gathered around a little girl who was"
  ]
}
```

# How To

```
# By default this IaC will not build or deploy anything. 

# To prepare your Pulumi stack, run the following commands:

   1. gh repo clone usrbinkat/katwalk && cd katwalk
   2. python3 -m venv venv
   3. source venv/bin/activate
   4. python -m pip install --upgrade pip setuptools wheel
   5. python -m pip install -r requirements.txt
   6. pulumi login file://~/.pulumi/state
   7. pulumi stack init

# To deploy locally on Docker

   8. pulumi config set deploy True

# Running the container locally defaults to creating and using a Docker Volume to store LLM Models
# To override this with a local path set the full global path to your chosen directory
# >>  NOTICE: LLM Models consume 30 to 100 gigabytes of disk space or more!
# >>          Ensure you have sufficient storage available before proceeding.

   8. pulumi config set modelsPath /GLOBAL/PATH/TO/DIRECTORY

# To deploy in the cloud on Azure Container Instances

   8. pulumi config set runtime azure

# To build the image:

   9. pulumi config set imageBuild True # Defaults to False
  10. pulumi config set registry ghcr.io
  11. pulumi config set registryNamespace $NAMESPACE # this may be the same as your username
  12. pulumi config set password --secret <registry_password_or_api_token>
  13. pulumi config set username $USERNAME

# To skip pushing the image to a registry:

  14. pulumi config set skipImageUpload True

# To authenticate with huggingface.co to download llm model(s)

  15. pulumi config set --secret hfToken <huggingface_api_token>

Finally, run `pulumi up` to build, publish, and deploy as per your config settings!

When you are done, run `pulumi destroy` to deprovision your katwalk service.
```

# What's Next?
- Adding an API Gateway service?
- Adding vector database support?
- Add support for more types of models?
- https://github.com/mckaywrigley/chatbot-ui
- https://medium.com/microsoftazure/custom-chatgpt-with-azure-openai-9bee437ef733

# ADDITIONAL RESOURCES:
- https://towardsdatascience.com/vllm-pagedattention-for-24x-faster-llm-inference-fdfb1b80f83
- https://kaitchup.substack.com
- https://hamel.dev
- https://github.com/michaelthwan/llm_family_chart/blob/master/2023_LLMfamily.drawio.png
- https://kaiokendev.github.io/context

# Configuration Index
```
# Global Settings
deploy_service = True/False whether to deploy the katwalk server or not (optional)
container_runtime = defaults to docker (supported: azure / docker)

# Katwalk Server Container Image Build Settings
build_image = True/False aka: whether to build the image yourself (optional)
image_skip_push = True/False aka: this bool is backwards due to pulumi provider
registry_server = default: ghcr.io aka which container registry to push image to
registry_username = user account for the container registry
registry_namespace = project or namespace the container image should push to, may be same as registry_username

# HuggingFace
hfToken = api authentication token
hfUsername = username
hfModel = $publisher/$model name of the model aka repository that you want

# Docker Runtime (if running locally)
models_path = global path to local model storage directory (optional)
registry_password = katwalk container image registry auth token or password
```