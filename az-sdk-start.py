from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.storage.blob import BlobServiceClient
import os
import config

#azure_subscription_id = config.AZURE_SUBSCRIPTION_ID
azure_subscription_id = os.environ["az_subscription"]
rg_name = "azpythonsdk"
az_loc = "uksouth"
storage_name = "azpythonsdksa0806"
container_name = "container-1"

try:
    creds = AzureCliCredential()
    resource_client = ResourceManagementClient(credential=creds, subscription_id=azure_subscription_id)

    if resource_client.resource_groups.check_existence(resource_group_name="azpythonsdk"):
        print("Resource group already exists")
    else:
        rg_result = resource_client.resource_groups.create_or_update(
        resource_group_name=rg_name, 
        parameters={"location": az_loc}
    )
        print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region"
)

except Exception as ex:
    print(ex)

try:
    storage_client = StorageManagementClient(credential=creds, subscription_id=azure_subscription_id)
    
    if len([item.name for item in storage_client.storage_accounts.list() if item.name == storage_name]) == 0:

        check_name_result = storage_client.storage_accounts.check_name_availability({"name" : storage_name})

        if not check_name_result.name_available:
            print(f"Global Storage account name {storage_name} already exists")
        else:
            poller = storage_client.storage_accounts.begin_create(
                resource_group_name=rg_name,
                account_name=storage_name,
                parameters={
                    "location": az_loc,
                    "kind": "StorageV2",
                    "sku": {"name": "Standard_LRS"}
                }
            )
            account_result = poller.result()
            print(f"Provisioned storage account {account_result.name}")
    else:
        print(f"Storage account {storage_name} already exists in resource group: {rg_name}")

except Exception as ex:
    print(ex)

try:
    if not [item.name for item in storage_client.blob_containers.list(resource_group_name=rg_name, account_name=storage_name) if item.name=="container-1"]:

        blob_client = storage_client.blob_containers.create(resource_group_name=rg_name,
                                                        account_name=storage_name,
                                                        container_name=container_name,
                                                        blob_container={})
    else:
        print(f"Container {container_name} already exists!")


except Exception as ex:
    print(ex)

try:
    blob_service_client = BlobServiceClient(account_url="https://azpythonsdksa0806.blob.core.windows.net/", credential=creds)
    container_client = blob_service_client.get_container_client(container=container_name)

    for item in container_client.list_blob_names():
        print(item)

    # with open(file="test.txt", mode="rb") as data:
    #     blob = container_client.upload_blob(name="test.txt", data=data, overwrite = True)

except Exception as ex:
    print(ex)