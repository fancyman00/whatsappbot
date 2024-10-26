import asyncio
import io
import tempfile


from app.config import settings

from moviepy.editor import VideoFileClip, AudioFileClip

from app.tools.http import make_download_request


class EvenLabs:

    def __init__(self):
        self._api_key = settings.VOICE.KEY
        self._headers = {
            "xi-api-key": f"{self._api_key}",
            "Content-Type": "application/json",
        }

    async def process_text_to_speech(
        self, text: str, max_attempts: int = 3
    ) -> io.BytesIO:
        url = "https://api.elevenlabs.io/v1/text-to-speech/V5y3lF5udiMrnKNgs3Yg"

        body = {
            "text": text,
            "voice_id": "V5y3lF5udiMrnKNgs3Yg",
            "voice_settings": {"stability": 0.1, "similarity_boost": 0.3, "style": 0.2},
        }

        for attempt in range(max_attempts):
            try:
                _, data = await make_download_request(
                    "POST", url, headers=self._headers, json=body
                )
                print(len(data))
                return io.BytesIO(data)
            except Exception as e:
                print(e)
                if attempt < max_attempts - 1:
                    await asyncio.sleep(5)
        raise Exception("All attempts to process text to speech have failed.")

    async def process_text_to_video(
        self, text: str, video_file_path: str
    ) -> io.BytesIO:
        audio_content = await self.process_text_to_speech(text)
        return overlay_audio_on_video(video_file_path, audio_bytes_io=audio_content)


async def get_evenlabs():
    return EvenLabs()


def overlay_audio_on_video(video_file_path, audio_bytes_io):
    video = VideoFileClip(video_file_path)

    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_audio_file:
        temp_audio_file.write(audio_bytes_io.read())
        temp_audio_path = temp_audio_file.name

    audio = AudioFileClip(temp_audio_path)

    video = video.set_audio(audio)

    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_video_file:
        temp_video_path = temp_video_file.name

    video.write_videofile(
        temp_video_path,
        codec="libx264",
        audio_codec="aac",
        fps=video.fps,
        remove_temp=True,
    )

    output_buffer = io.BytesIO()
    with open(temp_video_path, "rb") as temp_file:
        output_buffer.write(temp_file.read())

    output_buffer.seek(0)

    video.close()

    return output_buffer
