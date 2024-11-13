from azure.identity import AzureCliCredential
from azure.keyvault.secrets import SecretClient
from azure.storage.blob import BlobServiceClient
import config
import pyodbc

key_vault = config.KEY_VAULT

creds = AzureCliCredential()
secret_client = SecretClient(vault_url=key_vault, credential=creds)

server = secret_client.get_secret("sqlServer").value
database = secret_client.get_secret("database").value
user = secret_client.get_secret("user").value
password = secret_client.get_secret("pass").value


conn_string = "Driver={0};Server={1};Database={2};Uid={3};Pwd={4};".format("{ODBC Driver 17 for SQL Server}", server, database, user, password)


try:
    conn = pyodbc.connect(conn_string)

except pyodbc.Error as e:
    print(e)


else:
    cursor = conn.cursor()
    sql_statement = """
        SELECT [CourseID]
      ,[Title]
      ,[Topic]
      ,[Instructor]
      ,[Level]
  FROM [dbo].[OnlineCourses]
    """
    cursor.execute(sql_statement)
    records = list(cursor.fetchall())
    
    with open("results.csv", "w+") as data:
        data.write("CourseID,Title,Topic,Instructor,Level\n")
        for record in records:
            data.write(str(record).replace("(", "").replace(")", "")+"\n")

try:
    blob_service_client = BlobServiceClient(account_url="https://testingadls0806.blob.core.windows.net/", credential=creds)
    
    container_client = blob_service_client.get_container_client(container="container-func")

    with open(file="results.csv", mode="rb") as upload:
        blob = container_client.upload_blob(name="results.csv", data=upload, overwrite = True)

    for item in container_client.list_blob_names():
        print(item)

except Exception as ex:
    print(ex)