from db.requests.chats_requests import get_chats_to_reminder
from sqlalchemy.ext.asyncio import AsyncSession


class ReminderService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def chats_list_to_send(self, current_hour: int) -> list:
        """Should we send the reminder to chats"""
        return await get_chats_to_reminder(self.session, current_hour)
