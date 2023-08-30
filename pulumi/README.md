# KatWalk Server - Pulumi IaC

## About:

Katwalk server is a PoC to demonstrate cloud hosted LLM API and infrastructure orchestration.

Here you will find all "Infrastructure as Code" artifacts for building Katwalk Server and deploying to any supported runtime target.

By default this IaC will not build or deploy anything until the required build or deploy config values are set.

## Deployment options:
- Locally with Docker
- Runpod.io GPU Cloud (alpha)
- Azure on ACI*
- More to come

> Azure ACI containers take ~90 minutes to start for un-diagnosed reasons

## Prerequisites:

Requirements:

* [Pulumi](https://www.pulumi.com/docs/install/)
* [Python3](https://www.python.org/downloads/)
* [Git CLI](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [Huggingface Token](https://huggingface.co/docs/transformers.js/guides/private)
* [Huggingface access to LLaMa2](https://huggingface.co/meta-llama)
  * [Meta LLaMa2 Access](https://ai.meta.com/resources/models-and-libraries/llama-downloads/)

Optional Requirements (must choose one)

* [Docker](https://docs.docker.com/engine/install/)
  * [Nvidia CUDA Enabled GPU](https://developer.nvidia.com/cuda-gpus)
  * [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
* [Azure](https://azure.microsoft.com/en-us)
  * [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
* [Runpod.io](https://runpod.io)
  * [Runpod api key](https://docs.runpod.io/docs/graphql-api)

### 1. Prepare your Pulumi IaC Directory:

```bash
# Clone the repository and cd to the pulumi iac directory
gh repo clone usrbinkat/katwalk && cd katwalk/pulumi

# Create and initialize the python virtual env
python3 -m venv venv && source venv/bin/activate

# Install python dependencies
python -m pip install -r requirements.txt
```

### 2. Login & Initialize your pulumi state file and stack

```bash
# Create & Export a pulumi secret decryption password file
# This allows for decrypting any secrets in your Pulumi.<stack>.yaml file
# !WARNING! Please use a more secure password than this example.
export PULUMI_CONFIG_PASSPHRASE_FILE=$HOME/.pulumi/secret
echo "keepItSecretKeepItSafePassword" > ~/.pulumi/secret

# There are many ways to store pulumi state, here we use a local file.
# Other state backends include s3, Pulumi Cloud, and more.
pulumi login file://~/.pulumi

# Initialize your stack
# Here we name the stack "dev"
pulumi stack init --stack dev
```


### 3. Configure Huggingface credentials

```bash
# Set Huggingface.co username
pulumi config set hfUser <huggingface_username>

# Configure token as secret
pulumi config set --secret hfToken <huggingface_api_token>

# Set the model that you want to download
pulumi config set hfModel "meta-llama/Llama-2-7b-chat-hf"
```

### opt.A. Deploy locally with Docker

> !WARNING!    
> LLM Models can use up 30 to 100 gigabytes of disk space or more!    
> Ensure you have sufficient free disk space before proceeding.

```bash
# This enables the IaC to deploy Katwalk Server
pulumi config set deploy True

# Set the deploy runtime to docker to deploy locally
pulumi config set runtime docker

# (OPTIONAL): set a local directory to store llm model(s)
# If you do not set this path then Pulumi will fallback to
# provision and utilize a docker volume for model storage.
pulumi config set modelsPath /home/kat/models

# Finally, run `pulumi up` to deploy!
pulumi up

# When done, you can 'destroy' the stack to deprovision your deployment
pulumi destroy
```

### opt.B. Deploy in the cloud on Azure Container Instances

```bash
# This enables the IaC to deploy Katwalk Server
pulumi config set deploy True

# Set the deploy runtime to docker to deploy locally
pulumi config set runtime azure

# Finally, run `pulumi up` to deploy!
pulumi up

# When done, you can 'destroy' the stack to deprovision your deployment
pulumi destroy
```

### opt.C. Build the Katwalk Container

```bash
# Set image build to True
# Optionally enable push to publish to a registry
pulumi config set dockerBuild True
pulumi config set dockerPush True

# Set registry and image location
# This should be compatible with any OCI registry
# - docker.io
# - ghcr.io
# - etc
pulumi config set dockerRegistry ghcr.io
pulumi config set dockerUser usrbinkat

pulumi config set dockerRegistrySecret --secret <registry_password_or_api_token>

pulumi up
```

```bash
# ACTUAL DEMO

kat@cuda:~$ curl -s -X 'POST' 'http://localhost:8000/v1/chat' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"prompt": "Tell me a story about a little robot."}' | jq .
{
  "text": [
    "\nOnce upon a time, there was a little robot named R2. R2 was a friendly and curious robot who lived in a big city. One day, R2 decided to go on an adventure. He set out to explore the city and learn about all the different things he could see and do.\nAs R2 explored the city, he met all kinds of people. Some were kind and welcoming, while others were scared or suspicious of him. Despite this, R2 continued to be friendly and curious, always asking questions and trying to learn more about the world around him.\nOne day, while R2 was exploring a busy market, he saw a group of people gathered around a little girl who was"
  ]
}
```

-------------------------------------------------------------------------

# Configuration Index
```yaml
# secret encryption salt
encryptionsalt: v1:Ce8NM940=:v1:j+XGC73Zqp:t34XyjytvHcK+G1luA==
config:

  #################################################################
  # General Deploy config
  #################################################################
  # Usage Keys:
  #   Keys:
  #     - pulumi config set <key> <value>
  #   Secret Keys:
  #     - pulumi config set --secret <secret_key> <secret_value>

  katwalk:deploy: "True" # Default: False, set to "True" to deploy
  katwalk:runtime: "runpod" # Default: docker, accepts: docker, runpod, azure
  katwalk:deploymentName: "katwalk" # Defaults to "katwalk"

  #################################################################
  # Docker Image Settings
  #################################################################

  # Docker Build & Push Settings
  katwalk:dockerBuild: "False" # Default: False, set to "True" to build container
  katwalk:dockerPush: "False" # Default: False, set to "True" to push container

  # Docker Image Name & Registry Settings
  katwalk:dockerTag: "20230829"
  katwalk:dockerName: "katwalk"
  katwalk:dockerProject: "usrbinkat" # Optional if same as dockerUser
  katwalk:dockerRegistry: "ghcr.io" # accepts: any oci registry service (e.g. ghcr.io, docker.io, etc.)

  # Registry Credentials
  katwalk:dockerUser: "usrbinkat"

  # Optional unless pushing to registry or deploying to Azure
  katwalk:dockerRegistrySecret: # accepts: oci registry api token or password as `pulumi config set --secret dockerRegistrySecret <token>`
    secure: v1:UUt+00x+9Tz1:IVMKQ/2J+5ydq5R/kuFlfp+v5yYDF8HcL3Vy9Vz8nTNKPU=

  #################################################################
  # Huggingface Settings
  #################################################################

  # Huggingface Model ID string
  katwalk:hfModel: "meta-llama/Llama-2-7b-chat-hf" # accepts: any `hf` format Huggingface model ID

  # Huggingface Credentials
  katwalk:hfUser: "usrbinkat" # accepts: Huggingface user name
  katwalk:hfToken: # accepts: Huggingface API auth token as `pulumi config set --secret hfToken <token>`
    secure: v1:5hwLBQ4KO:/DNzuZ7UfbMMOQGxF7d29a+nWm04YSspPDm11y79E=

  #################################################################
  # Docker Deploy Settings
  #################################################################

  # If deploying locally via Docker
  # Default: create & use docker volume
  # Optional: set global local host path to models directory
  katwalk:modelsPath: /home/kat/models

  #################################################################
  # Azure Deploy Settings
  #################################################################

  katwalk:azureAciGpu: "V100" # accepts: V100, K80, P100
  katwalk:azureAciGpuCount: "1" # accepts: 1, 2, 4, 8

  #################################################################
  # Runpod Deploy Settings
  #################################################################

  # Runpod GPU Type
  # List of available GPU types in ./doc/runpod/README.md
  katwalk:runpodGpuType: "NVIDIA RTX A6000" # accepts: any valid Runpod GPU type

  # Runpod Credentials
  katwalk:runpodToken:
    secure: v1:2IqzPVRePwRwz:KbJzp+5L+khtSBbgW6FjPpdCQszP700xJAZVcrg/qBoo/pbgK=

```