import datetime, pytz, os
from azure.storage.blob import BlobServiceClient

# Values to edit
## Container name starts with "bootdiagnostics-", example: bootdiagnostics-vmname-abc123
CONTAINER_NAME_STARTS_WITH = "bootdiagnostics-"
## All containers last edited before this date will be deleted
LAST_EDIT_DATE = "2024-02-02"

def delete_containers(BLOB_CONNECTION_STRING):
    try:
        with open("output.txt", "a") as file:
            tz = pytz.timezone('UTC')
            last_edit_date_max = tz.localize(datetime.datetime.strptime(LAST_EDIT_DATE, "%Y-%m-%d"))
            blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)

            container_list = blob_service_client.list_containers()

            for container in container_list:
                container_client = blob_service_client.get_container_client(container.name)
                properties = container_client.get_container_properties()
                last_modified = properties['last_modified']
                # If the container name starts with "bootdiagnostics-" and last modified date is before 2024, then delete the container
                if container.name.startswith(CONTAINER_NAME_STARTS_WITH) and last_modified < last_edit_date_max:
                    print(f"Container name: {container.name}, Last modified: {last_modified}")
                    file.write(f"Container name: {container.name}, Last modified: {last_modified}\n")

            delete = input("Please confirm with the file output.txt that you want to delete the containers. Type 'yes' to delete: ")

            if delete == "yes":
                for container in container_list:
                    container_client = blob_service_client.get_container_client(container.name)
                    properties = container_client.get_container_properties()
                    last_modified = properties['last_modified']
                    if container.name.startswith(CONTAINER_NAME_STARTS_WITH) and last_modified < last_edit_date_max:
                        print(f"Deleting container: {container.name}")
                        container_client.delete_container()

    except Exception as e:
        print(e)

def get_connection_string_variable():
    BLOB_CONNECTION_STRING = os.getenv("BLOB_CONNECTION_STRING")
    if not BLOB_CONNECTION_STRING:
        raise ValueError("BLOB_CONNECTION_STRING environment variable is not set")
    return BLOB_CONNECTION_STRING

if __name__ == '__main__':
    delete_containers(get_connection_string_variable())