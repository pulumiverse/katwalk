from pulumi_azure_native import storage as native_storage
from pulumi_azure_native import resources as azr
import pulumi_azure_native.containerinstance as aci
from pulumi import Output

def azure_aci(
        project_name,
        config_hf_user,
        config_hf_token,
        config_hf_model_id,
        config_azure_aci_gpu,
        config_azure_aci_gpu_count,
        config_docker_name_full,
        config_oci_project,
        config_oci_secret,
        config_oci_server,
        region
    ):
    print("[./azure/aci.py=azure_aci] Deploying container in the cloud with Azure ...")

    # Create a resource group
    resource_group_name = f"{project_name}-rg"
    resource_group = azr.ResourceGroup(
        resource_group_name,
        location=region,
        tags={
            "app": project_name,
        }
    )

    # Create a storage account
    storage_account = native_storage.StorageAccount(
        project_name,
        resource_group_name=resource_group.name,
        location=resource_group.location,
        kind=native_storage.Kind.STORAGE_V2,
        sku=native_storage.SkuArgs(
            name="Standard_GRS"
        ),
        tags={
            "app": project_name,
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
    file_share = native_storage.FileShare(
        project_name,
        resource_group_name=resource_group.name,
        account_name=storage_account.name
    )

    # Create and expose a container group with a GPU-enabled container
    container_group = aci.ContainerGroup(
        project_name,
        os_type="Linux",
        location=resource_group.location,
        resource_group_name=resource_group.name,
        containers=[aci.ContainerArgs(
            name=project_name,
            image=config_docker_name_full,
            resources=aci.ResourceRequirementsArgs(
                requests=aci.ResourceRequestsArgs(
                    cpu=4.0,
                    memory_in_gb=16,
                    gpu=aci.GpuResourceArgs(
                        count=config_azure_aci_gpu_count,
                        sku=config_azure_aci_gpu
                    )
                ),
                limits=aci.ResourceLimitsArgs(
                    cpu=4.0,
                    memory_in_gb=16,
                    gpu=aci.GpuResourceArgs(
                        count=config_azure_aci_gpu_count,
                        sku=config_azure_aci_gpu
                    )
                ),
            ),
            command=["python", "main.py"],
            environment_variables=[
                {"name": "HF_USER", "value": config_hf_user},
                {"name": "HF_REPO", "value": config_hf_model_id},
                {"name": "HF_TOKEN", "value": config_hf_token.apply(lambda token: f"{token}")},
                {"name": "REFRESH_REPOSITORIES", "value": "True"}
            ],
            ports=[aci.ContainerPortArgs(
                port=8000,
                protocol="TCP"
            )],
            volume_mounts=[aci.VolumeMountArgs(
                name=f"{project_name}-model-volume",
                mount_path="/models"
            )],
        )],
        volumes=[aci.VolumeArgs(
            name=f"{project_name}-model-volume",
            azure_file=aci.AzureFileVolumeArgs(
                share_name=file_share.name,
                storage_account_name=storage_account.name,
                storage_account_key=primary_access_key,
            )
        )],
        ip_address=aci.IpAddressArgs(
            ports=[aci.PortArgs(
                protocol="TCP",
                port=8000
            )],
            type="Public",
            dns_name_label=project_name
        ),
        image_registry_credentials=[aci.ImageRegistryCredentialArgs(
            server=config_oci_server,
            username=config_oci_project,
            password=config_oci_secret.apply(lambda token: f"{token}")
        )]
    )

    # Stack exports
    return container_group.name
