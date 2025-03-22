import os
import requests
from dotenv import load_dotenv

load_dotenv()

class NetbirdAPI:
    def __init__(self):
        self.api_key = os.getenv("NETBIRD_API_KEY")
        self.base_url = os.getenv("NETBIRD_API_URL")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def block_user(self, user_id: str) -> bool:
        """Блокировка пользователя в Netbird"""
        try:
            response = requests.put(
                f"{self.base_url}/users/{user_id}/block",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error blocking user in Netbird: {e}")
            return False

    def unblock_user(self, user_id: str) -> bool:
        """Разблокировка пользователя в Netbird"""
        try:
            response = requests.put(
                f"{self.base_url}/users/{user_id}/unblock",
                headers=self.headers
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error unblocking user in Netbird: {e}")
            return False

    def get_user_status(self, user_id: str) -> dict:
        """Получение статуса пользователя"""
        try:
            response = requests.get(
                f"{self.base_url}/users/{user_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"Error getting user status from Netbird: {e}")
            return None 