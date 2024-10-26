import random
from typing import Sequence

import httpx

from app.models.message import Messages

from app.config import settings


class OpenAI:

    def __init__(self):
        self._base_api = settings.GPT.URL
        self._headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {settings.GPT.KEY}",
                "X-Title": "NeatStudio"
            }
        self._proxy = "socks5://a84aJOmrsA:UrfpnsCJJR@77.221.143.217:56749"
        self._model = "gpt-4o"

    async def _post(self, url: str, body: dict) -> dict:  # TODO: REMOVE

        async with httpx.AsyncClient(timeout=250, proxies=self._proxy) as client:
            response = await client.post(
                f"{self._base_api}{url}", headers=self._headers, json=body
            )
            answer = response.json()
        return answer

    async def _set_memories(
        self, content: str, memories: Sequence[Messages] | None
    ) -> list[dict[str, str]]:
        messages = [
            {
                "role": "system",
                "content": settings.GPT.PROMPT.replace(
                    "%random_number%", f"{random.randint(1, 10000)}"
                ),
            }
        ]
        if memories:
            for memory in memories:
                user_message = {"role": "user", "content": memory.message}
                chat_message = {"role": "assistant", "content": memory.answer}

                if memory.answer:
                    messages.extend([chat_message])
                if memory.message:
                    messages.extend([user_message])

        user_prompt = {"role": "user", "content": content}
        messages.append(user_prompt)
        return messages

    async def generate_message(
        self,
        content: str,
        memories: Sequence[Messages] | None,
    ): # TODO: REFACTOR FOR AIOHTPP
        messages = await self._set_memories(content, memories)

        url = "/chat/completions"
        body = {
            "model": self._model,
            "messages": messages,
        }
        response = await self._post(url=url, body=body)

        answer = response.get("choices")[0].get("message").get("content")

        return answer


async def get_open_ai() -> OpenAI:
    return OpenAI()


