# KatWalk Server - Pulumi IaC

## About:

Katwalk server is a PoC to demonstrate cloud hosted LLM API and infrastructure orchestration.

Here you will find all "Infrastructure as Code" artifacts for building Katwalk Server and deploying either locally with docker or in the cloud on Azure Container Instances. By default this IaC will not build or deploy anything until the required build or deploy config values are set.

## Limitations: 

*Models*: currently Katwalk is only tested to run `hf` format models from huggingface repositories.

*Platforms*: linux/amd64 is the architecture tested so far.

Encouragement and or PRs for enhancements are welcome!

## Prerequisites:

Requirements:

* [Pulumi](https://www.pulumi.com/docs/install/)
* [Python3](https://www.python.org/downloads/)
* [Git CLI](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [Huggingface Token](https://huggingface.co/docs/transformers.js/guides/private)
* [Huggingface access to LLaMa2](https://huggingface.co/meta-llama)
  * [Meta LLaMa2 Access](https://ai.meta.com/resources/models-and-libraries/llama-downloads/)

> !NOTE! Access to LLaMa2 via Huggingface is not required if using a non-private model repository. Learn more [HERE](https://huggingface.co/docs/transformers.js/guides/private)

Optional Requirements (must choose one)
* [Docker](https://docs.docker.com/engine/install/)
  * [Nvidia Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
  * [Nvidia CUDA Enabled GPU](https://developer.nvidia.com/cuda-gpus)
* [Azure](https://azure.microsoft.com/en-us)
  * [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)


### 1. Prepare your Pulumi IaC Directory:

```bash
# Clone the repository and cd to the pulumi iac directory
gh repo clone usrbinkat/katwalk && cd katwalk/pulumi

# Create and initialize the python virtual env
python3 -m venv venv && source venv/bin/activate

# Install python dependencies
python -m pip install -r requirements.txt
```

## 2. Login & Initialize your pulumi state file and stack

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


# Configure required credentials
```bash
# Set Huggingface.co username
pulumi config set hfUsername <huggingface_username>

# Configure token as secret
pulumi config set --secret hfToken <huggingface_api_token>

# Set the model that you want to download
pulumi config set hfModel "meta-llama/Llama-2-7b-chat-hf"
```
# Deploy locally with Docker

```bash
# This enables the IaC to deploy Katwalk Server
pulumi config set deploy True

# Set the deploy runtime to docker to deploy locally
pulumi config set runtime docker

# (OPTIONAL): set a local directory to store llm model(s)
pulumi config set modelsPath /home/kat/models

# Finally, run `pulumi up` to deploy!
pulumi up

# When done, you can 'destroy' the stack to deprovision your deployment
pulumi destroy
```

## Build the Katwalk Container

```bash
# Set image build to True
pulumi config set imageBuild True # Defaults to False

# Set registry and image location
# This should be compatible with any OCI registry
# - private registry
# - docker.io
# - quay.io
pulumi config set registry ghcr.io
pulumi config set registryNamespace usrbinkat

pulumi config set password --secret <registry_password_or_api_token>
pulumi config set username $USERNAME

kip pushing the image to a registry:

pulumi config set skipImageUpload True
```
# Running the container locally defaults to creating and using a Docker Volume to store LLM Models
# To override this with a local path set the full global path to your chosen directory
# >>  NOTICE: LLM Models consume 30 to 100 gigabytes of disk space or more!
# >>          Ensure you have sufficient storage available before proceeding.


# To deploy in the cloud on Azure Container Instances


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
