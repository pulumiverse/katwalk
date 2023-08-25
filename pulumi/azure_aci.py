from pulumi_azure_native import storage, containerinstance
from pulumi import Output
import azure as azure

def azure_aci(username, model, download_list, hf_token, image_name, image_name_full, password, location="East US", resource_group_name="myResourceGroup"):

    # Extract the string value of hf_token
    hf_token_str = Output.from_input(hf_token).apply(lambda token: f"HF_TOKEN={token}")

    # Create a resource group
    resource_group = azure.core.ResourceGroup(resource_group_name, location=location)

    # Create a storage account
    storage_account = azure.storage.Account(image_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        account_tier="Standard",
        account_replication_type="GRS",
        tags={
            "app": "katwalk",
        }
    )

    # Create a file share in the storage account
    file_share = storage.Share(image_name, account_name=storage_account.name)

    # Create a container group with GPU-enabled container
    container_group = azure.containerservice.Group(image_name,
        location=resource_group.location,
        resource_group_name=resource_group.name,
        ip_address_type="Public",
        dns_name_label="katwalk",
        os_type="Linux",
        containers=[
            azure.containerservice.GroupContainerArgs(
                name=image_name,
                image=image_name_full,
                cpu=2.0,
                memory=4,
                ports=[azure.containerservice.GroupContainerPortArgs(
                    port=8000,
                    protocol="TCP"
                )],
                resources=containerinstance.ResourceRequirementsArgs(
                    requests=containerinstance.ResourceRequestsArgs(
                    ),
                    limits=containerinstance.ResourceLimitsArgs(
                        gpu=containerinstance.GpuResourceArgs(count=1, sku="K80") # Requesting 1 GPU
                    ),
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
