from pulumi_azure_native import storage as native_storage
from pulumi_azure_native import resources as azr
import pulumi_azure_native.containerinstance as aci
from pulumi import Output

def azure_aci(
        username,
        model,
        hf_token,
        image_name,
        image_name_full,
        password,
        location,
        resource_group_name,
        dns_name_label="katwalk"
    ):

    # Extract string values of hf_token and password
    hf_token_str = Output.from_input(hf_token).apply(lambda token: f"{token}")
    password_str = Output.from_input(password).apply(lambda token: f"{token}")

    # Create a resource group
    resource_group = azr.ResourceGroup(resource_group_name, location=location)

    # Create a storage account
    storage_account = native_storage.StorageAccount(image_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        kind=native_storage.Kind.STORAGE_V2,
        sku=native_storage.SkuArgs(
            name="Standard_GRS"
        ),
        tags={
            "app": "katwalk",
        }
    )

    # Get the storage account keys using the resource group and storage account
    storage_account_keys = Output.all(resource_group.name, storage_account.name).apply(
        lambda args: native_storage.list_storage_account_keys(
            resource_group_name=args[0],
            account_name=args[1]
        )
    )

    # Get the primary key
    primary_access_key = storage_account_keys.apply(lambda keys: keys.keys[0].value)

    # Create a file share in the storage account
    file_share = native_storage.FileShare(image_name,
        resource_group_name=resource_group.name,
        account_name=storage_account.name
    )

    # Create and expose a container group with a GPU-enabled container
    container_group = aci.ContainerGroup(image_name,
        location=resource_group.location,
        resource_group_name=resource_group.name,
        os_type="Linux",
        ip_address=aci.IpAddressArgs(
            ports=[aci.PortArgs(
                protocol="TCP",
                port=8000
            )],
            type="Public",
            dns_name_label=dns_name_label,
        ),
        image_registry_credentials=[aci.ImageRegistryCredentialArgs(
            server="ghcr.io",
            username=username,
            password=password_str
        )],
        volumes=[aci.VolumeArgs(
            name="models",
            azure_file=aci.AzureFileVolumeArgs(
                share_name=file_share.name,
                storage_account_name=storage_account.name,
                storage_account_key=primary_access_key,
            )
        )],
        containers=[aci.ContainerArgs(
            name=image_name,
            image=image_name_full,
            resources=aci.ResourceRequirementsArgs(
                requests=aci.ResourceRequestsArgs(
                    cpu=4.0,
                    memory_in_gb=16,
                    gpu=aci.GpuResourceArgs(count=1, sku="V100")  # Requesting 1 GPU
                ),
                limits=aci.ResourceLimitsArgs(
                    gpu=aci.GpuResourceArgs(count=1, sku="V100")  # Limiting to 1 GPU
                ),
            ),
            environment_variables=[
                {"name": "REFRESH_REPOSITORIES", "value": "True"},
                {"name": "HF_USER", "value": username},
                {"name": "HF_REPO", "value": model},
                {"name": "HF_TOKEN", "value": hf_token_str},
            ],
            command=["python", "main.py"],
            ports=[aci.ContainerPortArgs(
                port=8000,
                protocol="TCP"
            )],
            volume_mounts=[aci.VolumeMountArgs(
                name="models",
                mount_path="/models"
            )],
        )]
    )

    # Stack exports
    return container_group.name
