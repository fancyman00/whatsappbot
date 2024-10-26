import io

from app.config import settings
from app.tools.http import make_request


class ChatAPI:

    def __init__(self):
        self._base_url = f"{settings.CHAT.URL}/waInstance{settings.CHAT.ID_INSTANCE}"
        self._token_instance = settings.CHAT.TOKEN_INSTANCE
        self._headers = {
            "Content-Type": "application/json",
        }

    async def send_message(self, to: str, message: str) -> None:
        url = f"{self._base_url}/sendMessage/{self._token_instance}"
        body = {
            "chatId": f"{to}@c.us",
            "message": message,
        }
        response, data = await make_request(
            "POST", url, headers=self._headers, json=body
        )

        if response.status_code != 200:  # todo на время разрабокти
            print(f"Ошибка при отправке сообщения: {response.text}")

    async def upload_file(self, file: bytes, type: str) -> dict:
        url = f"{self._base_url}/uploadFile/{self._token_instance}"
        headers = {
            "Authorization": f"Bearer {self._token_instance}",
            "Content-Type": type,
        }
        response, data = await make_request("POST", url, headers=headers, data=file)

        return data["urlFile"]

    async def send_video(self, to: str, file: io.BytesIO) -> None:
        file_url = await self.upload_file(file.read(), type="video/mp4")
        url = f"{self._base_url}/sendFileByUrl/{self._token_instance}"
        data = {
            "fileName": f"{to}.mp4",
            "urlFile": file_url,
            "chatId": f"{to}@c.us",
        }
        response, data = await make_request(
            "POST", url, headers=self._headers, json=data
        )

    async def send_audio(self, to: str, file: io.BytesIO) -> None:
        file_url = await self.upload_file(file.read(), type="application/ogg")
        url = f"{self._base_url}/sendFileByUrl/{self._token_instance}"
        data = {
            "fileName": f"{to}.ogg",
            "urlFile": file_url,
            "chatId": f"{to}@c.us",
        }
        response, data = await make_request(
            "POST", url, headers=self._headers, json=data
        )

    async def get_messages(self) -> tuple[str, str]:
        url = f"{self._base_url}/receiveNotification/{self._token_instance}"
        params = {"receiveTimeout": 5}
        response, data = await make_request(
            "GET", url, headers=self._headers, params=params, timeout=20
        )
        await self.delete_message(data["receipt_id"])
        return data

    async def delete_message(self, receipt_id: str) -> None:
        url = f"{self._base_url}/deleteNotification/{self._token_instance}/{receipt_id}"
        await make_request("DELETE", url, headers=self._headers)

    async def get_user_message(self, data: dict) -> tuple[str, str]:
        sender: str | None = data.get("senderData", {}).get("sender", None)
        message_data: dict | None = data.get("messageData", None)

        if sender:
            sender = sender.split("@")[0] or None

        if message_data and message_data.get("typeMessage", None) == "textMessage":
            text = message_data.get("textMessageData", {}).get("textMessage", None)

        return sender, text


def get_chat_api() -> ChatAPI:
    return ChatAPI()
