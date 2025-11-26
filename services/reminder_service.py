from db.repositories.chats import ChatsRepository


class ReminderService:
    def __init__(self, chats_repo: ChatsRepository):
        self.chats_repo = chats_repo

    async def chats_list_to_send(self, current_hour: int) -> list:
        """Should we send the reminder to chats"""
        return await self.chats_repo.get_chats_to_reminder(current_hour)
