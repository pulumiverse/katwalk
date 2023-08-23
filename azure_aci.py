from pulumi_azure_native import storage
from pulumi_azure_native.storage import StorageAccount, Share
from pulumi_azure_native.containerservice import Volume, VolumeArgs, VolumeMount, ContainerPort, ContainerArgs, ContainerGroup, VolumeMountArgs, ContainerPortArgs, ContainerGroupArgs, ResourceRequestsArgs, ImageRegistryCredential, ResourceRequirementsArgs

def azure_aci(username, model, download_list, hf_token, image_name_full, location, resource_group_name, storage_account_name, file_share_name):

    # Create a storage account
    storage_account = StorageAccount(image_name,
        sku=storage.SkuArgs(name="Standard_LRS"),
        kind="StorageV2",
        location=location,
    )

    # Create a file share in the storage account
    file_share = Share(image_name, account_name=storage_account.name)

    # Extract the string value of hf_token
    hf_token_str = hf_token.apply(lambda token: f"HF_TOKEN={token}")

    # Create a container group with GPU-enabled container
    container_group = ContainerGroup(
        resource_name=image_name,
        args=ContainerGroupArgs(
            location=location,
            os_type="Linux",
            containers=[
                ContainerArgs(
                    name=image_name,
                    image=image_name_full,
                    resources=ResourceRequestsArgs(
                        requests=ResourceRequestsArgs(
                            cpu=1.0,
                            memory_in_gb=4
                        )
                    ),
                    ports=[
                        ContainerPort(
                            port=8000
                        )
                    ],
                    environment_variables=[
                        {"name": "REFRESH_REPOSITORIES", "value": "True"},
                        {"name": "HF_USER", "value": username},
                        {"name": "HF_REPO", "value": model},
                        {"name": "HF_REPOS", "value": download_list},
                        {"name": "HF_TOKEN", "value": hf_token}
                    ],
                    volume_mounts=[
                        VolumeMount(
                            name="modelstorage",
                            mount_path="/models"
                        )
                    ],
                    command=[
                        "python3",
                        "/katwalk/main.py"
                    ]
                )
            ],
            volumes=[
                Volume(
                    name="modelstorage",
                    azure_file=AzureFileVolumeArgs(
                        share_name=file_share_name,
                        read_only=False,
                        storage_account_name=storage_account_name
                    )
                )
            ],
            image_registry_credentials=[
                ImageRegistryCredential(
                    server="ghcr.io",
                    username=username,
                    password=password
                )
            ]
        )
    )
    
def azure_aci(username, model, download_list, hf_token, image_name, image_name_full, location="East US"):
    # Create a storage account
    storage_account = StorageAccount(image_name,
        sku=storage.SkuArgs(name="Standard_LRS"),
        kind="StorageV2",
        location=location,
    )

    # Create a file share in the storage account
    file_share = Share(image_name, account_name=storage_account.name)

    # Extract the string value of hf_token
    hf_token_str = hf_token.apply(lambda token: f"HF_TOKEN={token}")

    # Create a container group with GPU-enabled container
    container_group = ContainerGroup(
        resource_name=image_name,
        args=ContainerGroupArgs(
            containers=[
                ContainerArgs(
                    name=image_name,
                    image=image_name_full,
                    ports=[ContainerPortArgs(port=8000)], # Expose port 8000
                    resources=ResourceRequirementsArgs(
                        requests=ResourceRequestsArgs(
                            gpu=1, # Requesting 1 GPU
                            cpu=2.0, # CPU request
                            memory_in_gb=4 # Memory request
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
                    volume_mounts=[
                        VolumeMountArgs(
                            name="models",
                            mount_path="/models"
                        )
                    ],
                ),
            ],
            os_type="Linux",
            location=location, # Azure region
            ip_address=ContainerGroupArgs(
                ports=[ContainerPortArgs(port=8000)],
                type="Public" # Public IP
            ),
            volumes=[
                VolumeArgs(
                    name="models",
                    azure_file=VolumeArgs(
                        share_name=file_share.name,
                        storage_account_name=storage_account.name,
                        storage_account_key=storage_account.primary_access_key,
                    )
                )
            ]
        )
    )

    # Stack exports
    return container_group.name
