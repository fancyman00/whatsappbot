from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()


async def get_scheduler() -> AsyncIOScheduler:
    return scheduler
