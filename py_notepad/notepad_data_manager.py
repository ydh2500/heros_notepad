import requests
import json
import os
from urllib.parse import quote, unquote

class NotePadDataManager:
    def __init__(self, serial, local_file="tabs_data.json", server_url="http://192.168.5.118:9338", timeout=5):
        self.serial = serial
        self.local_file = local_file
        self.server_url = server_url
        self.timeout = timeout

    def sanitize_serial(self, serial: str) -> str:
        return quote(serial, safe='')

    def unsanitize_serial(self, serial: str) -> str:
        return unquote(serial)

    def save_to_local(self, data):
        with open(self.local_file, "w", encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        print("Tabs saved locally successfully.")

    def load_from_local(self):
        if os.path.exists(self.local_file):
            with open(self.local_file, "r", encoding='utf-8') as file:
                return json.load(file)
        return None

    def get_local_version(self):
        data = self.load_from_local()
        if data:
            return data.get("version", 0)
        return 0

    def load_from_server(self):
        try:
            sanitized_serial = self.sanitize_serial(self.serial)
            sanitized_serial = self.sanitize_serial(sanitized_serial)
            print(f"Requesting load from server with sanitized serial: {sanitized_serial}")
            response = requests.get(f"{self.server_url}/load_tabs/{sanitized_serial}", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Failed to load from server: {e}")
            return None

    def save_to_server(self, data):
        try:
            response = requests.post(f"{self.server_url}/save_tabs/", json=data, timeout=self.timeout)
            response.raise_for_status()
            print("Tabs saved on server successfully.")
            return response.json()["version"]
        except requests.exceptions.RequestException as e:
            print(f"Failed to save tabs on server: {e}")
            return None

    def sync_with_server(self, local_data):
        server_data = self.load_from_server()
        if server_data:
            server_serial = self.unsanitize_serial(server_data["tabs_data"]["serial"])
            local_serial = local_data.get("serial", "")
            if server_serial == local_serial:
                server_version = server_data["tabs_data"]["version"]
                local_version = local_data.get("version", 0)
                if server_version > local_version:
                    self.save_to_local(server_data["tabs_data"])
                    return server_data["tabs_data"]
                elif server_version < local_version:
                    updated_version = self.save_to_server(local_data)
                    if updated_version:
                        local_data["version"] = updated_version
                        self.save_to_local(local_data)
                else:
                    print("Local and server data are in sync.")
            else:
                print("Server data is for different serial.")
                #서버 데이터와 동기화
                self.save_to_local(server_data["tabs_data"])
                local_data = server_data["tabs_data"]
        else:
            print("Using local data as server has no data or server is unreachable.")
        return local_data



        #     if server_serial == local_serial:
        #     server_version = server_data["version"]
        #     print(f'server_version: {server_version}')
        #     print(f'local_data: {local_data}')
        #     print(f'local_version: {local_data["version"]}')
        #     if server_version > local_data["version"]:
        #         print("Updating local data to server version.")
        #         self.save_to_local(server_data["tabs_data"])
        #         return server_data["tabs_data"]
        #     elif server_version < local_data["version"]:
        #         print("Updating server data to local version.")
        #         updated_version = self.save_to_server(local_data)
        #         if updated_version:
        #             local_data["version"] = updated_version
        #             self.save_to_local(local_data)
        #     else:
        #         print("Local and server data are in sync.")
        # else:
        #     print("Using local data as server has no data or server is unreachable.")
        # return local_data

    def sync_on_startup(self):
        local_data = self.load_from_local() or {"version": 0}
        return self.sync_with_server(local_data)

    def get_serials_from_server(self):
        try:
            response = requests.get(f"{self.server_url}/list_serials/", timeout=self.timeout)
            response.raise_for_status()
            return [self.unsanitize_serial(serial) for serial in response.json().get("serials", [])]
        except requests.exceptions.RequestException as e:
            print(f"Failed to get serials from server: {e}")
            return []
