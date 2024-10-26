import asyncio
import datetime

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.message import Messages
from app.services.database import get_session
from app.services.green_api import ChatAPI, get_chat_api
from app.services.openai import OpenAI, get_open_ai


class MessageService:

    def __init__(self, session: AsyncSession, open_ai: OpenAI, chat_api: ChatAPI):
        self.session = session
        self.open_ai = open_ai
        self.chat_api = chat_api

    async def delayed_message(self, start_time: datetime, sender: str):
        await asyncio.sleep(settings.openai_setting.timeout)
        last_message = await Messages.get_last_message(sender)

        start_time = start_time.replace(tzinfo=datetime.timezone.utc)
        last_message = last_message.created_at.replace(tzinfo=datetime.timezone.utc)

        if last_message >= start_time + datetime.timedelta(minutes=5):
            return None

        memories = await self.get_messages(sender)

        promt = "I asked you a question above, but is there anything else you can say about this? Start writing something like this: I would like to add one more thing"
        response_text = await self.open_ai.generate_message(promt, memories, False)
        await self.green_api.send_message(sender, response_text)

    async def get_messages(self, sender: str):
        query = (
            select(Messages)
            .where(Messages.sender == sender)
            .order_by(Messages.created_at.desc())
            .limit(8)
        )  # todo у самого openai ограничение на 8 смс в истории
        _result = await self.session.execute(query)
        return _result.scalars().all()

    async def get_last_message(self, sender: str):
        query = (
            select(Messages)
            .where(Messages.sender == sender)
            .order_by(Messages.created_at.desc())
            .limit(1)
        )
        _result = await self.session.execute(query)
        return _result.scalars().all()

    async def get_number_of_message(self, sender):
        query = select(func.count(Messages.id)).where(Messages.sender == sender)

        _result = await self.session.execute(query)
        return _result.scalar()

    async def add_message(self, message: str, answer: str, sender: str):
        await Messages(message=message, answer=answer, sender=sender).save(
            db_session=self.session
        )


async def get_message_service(
    session: AsyncSession = Depends(get_session),
    green_api: ChatAPI = Depends(get_chat_api),
    open_ai: OpenAI = Depends(get_open_ai),
):
    return MessageService(session, green_api, open_ai)
