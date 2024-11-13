from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.storage import StorageManagementClient
import os
import config

#azure_subscription_id = config.AZURE_SUBSCRIPTION_ID
azure_subscription_id = os.environ["az_subscription"]
rg_name = "azpythonsdk"
az_loc = "uksouth"
storage_name = "azpythonsdksa0806"

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

    check_name_result = storage_client.storage_accounts.check_name_availability({"name" : storage_name})

    if not check_name_result.name_available:
        print(f"Storage account {storage_name} already exists")
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

except Exception as ex:
    print(ex)