import asyncio
from datetime import datetime, timedelta, timezone
import os
from fastapi import APIRouter, Depends, Request

from app.services.evenlabs import EvenLabs, get_evenlabs
from app.services.green_api import get_chat_api, ChatAPI
from app.services.message import MessageService, get_message_service
from app.services.openai import OpenAI, get_open_ai
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.scheduler import get_scheduler

router = APIRouter()


@router.post("/webhook")
async def webhook(
    request: Request,
    message_service: MessageService = Depends(get_message_service),
    green_api: ChatAPI = Depends(get_chat_api),
    open_ai: OpenAI = Depends(get_open_ai),
    even_lab: EvenLabs = Depends(get_evenlabs),
    scheduler: AsyncIOScheduler = Depends(get_scheduler),
):
    try:
        request_data: dict = await request.json()

        if request_data.get("typeWebhook", None) != "incomingMessageReceived":
            return

        sender, text = await green_api.get_user_message(request_data)

        number_of_message, memories = await asyncio.gather(
            message_service.get_number_of_message(sender),
            message_service.get_messages(sender),
        )
        answer_text = await open_ai.generate_message(text, memories)

        if (number_of_message + 1) % 5 == 0:
            byte_file = await even_lab.process_text_to_speech(answer_text)
            await green_api.send_audio(sender, byte_file)
        else:
            await green_api.send_message(sender, answer_text)
        # elif number_of_message == 1:
        #     file = os.path.join(
        #         os.path.dirname(__file__), "..", "assets", "input_video.mp4"
        #     )
        #     byte_file = await even_lab.process_text_to_video(answer_text, file)
        #     await green_api.send_video(sender, byte_file)

        now = datetime.now(timezone.utc)
        scheduler.add_job(
            message_service.delayed_message,
            "date",
            run_date=now + timedelta(minutes=5),
            args=[now, sender],
        )
        await message_service.add_message(
            message=text, answer=answer_text, sender=sender
        )

    except Exception as e:
        print(e)
        pass

    return 200
