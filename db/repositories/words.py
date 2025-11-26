import logging
from typing import Type, cast

from sqlalchemy import Date, and_, delete, func, literal_column, or_, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatCurrentWord, ChatStatistic, Status, Word
from db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class WordsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_word_by_id(self, word_id: int) -> Type[Word] | None:
        return await self.session.get(Word, {"word_id": word_id})

    async def add_current_chat_words(self, chat_id: int, interval_days: int, count: int) -> None:
        status_new = Status.new
        status_learned = Status.learned
        status_already_know = Status.already_know

        subquery = (
            select(Word.word_id)
            .outerjoin(
                ChatStatistic,
                and_(ChatStatistic.chat_id == chat_id, ChatStatistic.word_id == Word.word_id),
            )
            .filter(
                or_(
                    func.coalesce(ChatStatistic.status, status_new) == status_new,
                    and_(
                        or_(
                            func.coalesce(ChatStatistic.status, status_new) == status_learned,
                            func.coalesce(ChatStatistic.status, status_new) == status_already_know,
                        ),
                        (func.now().cast(Date) - ChatStatistic.status_date.cast(Date)) <= interval_days,
                    ),
                )
            )
            .order_by(func.random())
            .limit(count)
            .subquery()
        )

        # general request
        insert_stmt = upsert(ChatCurrentWord).from_select(
            ["chat_id", "word_id"], select(literal_column(str(chat_id)), subquery.c.word_id)
        )

        # insert
        await self.session.execute(insert_stmt)
        await self.session.commit()

    async def delete_current_word(self, chat_id: int, word_id: int):
        stmt = select(ChatCurrentWord).where(
            and_(ChatCurrentWord.chat_id == chat_id, ChatCurrentWord.word_id == word_id)
        )
        result = await self.session.execute(stmt)
        word = result.scalar()
        if word is not None:
            await self.session.delete(word)

    async def delete_random_current_words(self, chat_id: int, count: int):
        stmt = delete(ChatCurrentWord).where(
            and_(
                ChatCurrentWord.chat_id == chat_id,
                ChatCurrentWord.word_id.in_(
                    select(ChatCurrentWord.word_id)
                    .where(ChatCurrentWord.chat_id == chat_id)
                    .order_by(func.random())
                    .limit(count)
                ),
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def current_words_exists(self, chat_id: int) -> bool:
        stmt = select(ChatCurrentWord).where(ChatCurrentWord.chat_id == chat_id)
        result = await self.session.execute(stmt)
        word = result.scalar()
        return False if word is None else True

    async def get_words(self, chat_id: int, count: int, max_len: int | None = None) -> dict[str, list[Word]]:
        stmt = (
            select(Word)
            .join(ChatCurrentWord)
            .filter(ChatCurrentWord.chat_id == chat_id)
            .order_by(func.random())  # ORDER BY RANDOM()
            .limit(1)
        )

        if max_len is not None:
            stmt = stmt.where(func.length(func.trim(Word.word)) <= max_len)

        result = await self.session.execute(stmt)
        correct_word: Word = result.scalar()

        stmt = (
            select(Word)
            .where(Word.word_id != correct_word.word_id and Word.type == correct_word.type)
            .order_by(func.random())
            .limit(count)
        )

        result = await self.session.execute(stmt)
        variants = result.scalars().all()
        variants = cast(list[Word], variants)

        return dict(correct_word=correct_word, variants=variants)

    async def exists_short_word(self, chat_id: int, max_len: int) -> bool:
        stmt = (
            select(func.count())
            .select_from(ChatCurrentWord)
            .join(Word, Word.word_id == ChatCurrentWord.word_id)
            .where(
                ChatCurrentWord.chat_id == chat_id,
                func.length(func.trim(Word.word)) <= max_len,
            )
        )

        result = await self.session.execute(stmt)
        count = result.scalar_one()

        return count > 0
