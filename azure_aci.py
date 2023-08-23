from pulumi_azure_native import storage, containerinstance, resources
from pulumi import Output

def azure_aci(username, model, download_list, hf_token, image_name, image_name_full, password, location="East US", resource_group_name="myResourceGroup"):
    # Create a resource group
    resource_group = resources.ResourceGroup(resource_group_name, location=location)

    # Create a storage account
    storage_account = storage.StorageAccount(image_name,
        resource_group_name=resource_group.name,
        sku=storage.SkuArgs(name=storage.SkuName.STANDARD_LRS),
        kind=storage.Kind.STORAGE_V2,
        location=location,
    )

    # Create a file share in the storage account
    file_share = storage.Share(image_name, account_name=storage_account.name)

    # Extract the string value of hf_token
    hf_token_str = Output.from_input(hf_token).apply(lambda token: f"HF_TOKEN={token}")

    # Create a container group with GPU-enabled container
    container_group = containerinstance.ContainerGroup(image_name,
        resource_group_name=resource_group.name,
        location=location,
        os_type="Linux",
        containers=[containerinstance.ContainerArgs(
            name=image_name,
            image=image_name_full,
            ports=[containerinstance.ContainerPortArgs(port=8000)], # Expose port 8000
            resources=containerinstance.ResourceRequirementsArgs(
                requests=containerinstance.ResourceRequestsArgs(
                    cpu=2.0, # CPU request
                    memory_in_gb=4 # Memory request
                ),
                limits=containerinstance.ResourceLimitsArgs(
                    gpu=containerinstance.GpuResourceArgs(count=1, sku="K80") # Requesting 1 GPU
                )
            ),
            environment_variables=[
                {"name": "REFRESH_REPOSITORIES", "value": "True"},
                {"name": "HF_USER", "value": username},
                {"name": "HF_REPO", "value": model},
                {"name": "HF_REPOS", "value": download_list},
                {"name": "HF_TOKEN", "value": hf_token_str},
            ],
            command=["python3", "/katwalk/main.py"],
            volume_mounts=[containerinstance.VolumeMountArgs(
                name="models",
                mount_path="/models"
            )],
        )],
        volumes=[containerinstance.VolumeArgs(
            name="models",
            azure_file=containerinstance.AzureFileVolumeArgs(
                share_name=file_share.name,
                storage_account_name=storage_account.name,
                storage_account_key=storage_account.primary_access_key,
            )
        )],
        image_registry_credentials=[containerinstance.ImageRegistryCredentialArgs(
            server="ghcr.io",
            username=username,
            password=password
        )]
    )

    # Stack exports
    return container_group.name
