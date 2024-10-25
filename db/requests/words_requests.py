from db import Word
from db.models import UsersStatistic, Word, UserCurrentWord, Status
from sqlalchemy import select, and_, or_, func, literal_column, case, Interval, Date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert
from typing import cast, Type
import logging

logger = logging.getLogger(__name__)


async def get_word_by_id(
        session: AsyncSession,
        word_id: int
) -> Type[Word] | None:
    return await session.get(Word, {"word_id": word_id})


async def add_current_user_words(
        session: AsyncSession,
        user_id: int,
        interval_days: int,
        count: int) -> None:
    status_new = Status.new
    status_learned = Status.learned

    subquery = (
        select(Word.word_id)
        .outerjoin(
            UsersStatistic,
            and_(
                UsersStatistic.user_id == user_id,
                UsersStatistic.word_id == Word.word_id
            )
        )
        .filter(
            or_(
                func.coalesce(UsersStatistic.status, status_new) == status_new,
                and_(
                    func.coalesce(UsersStatistic.status, status_new) == status_learned,
                    (func.now().cast(Date) - UsersStatistic.status_date.cast(Date)) <= interval_days
                )
            )
        )
        .order_by(func.random())
        .limit(count)
        .subquery()
    )

    # general request
    insert_stmt = (
        upsert(UserCurrentWord).from_select(
            ['user_id', 'word_id'],
            select(literal_column(str(user_id)), subquery.c.word_id)
        )
    )

    # Выполняем вставку
    await session.execute(insert_stmt)
    await session.commit()


async def delete_current_word(
        session: AsyncSession,
        user_id: int,
        word_id: int
):
    stmt = select(UserCurrentWord).where(and_(UserCurrentWord.user_id == user_id,
                                              UserCurrentWord.word_id == word_id))
    result = await session.execute(stmt)
    word = result.scalar()
    if word is not None:
        await session.delete(word)


async def current_words_exists(
        session: AsyncSession,
        user_id: int
) -> bool:
    stmt = select(UserCurrentWord).where(UserCurrentWord.user_id == user_id)
    result = await session.execute(stmt)
    word = result.scalar()
    return False if word is None else True


async def get_words(
        session: AsyncSession,
        user_id: int,
        count: int
) -> dict[str:list[Word]]:
    "return words - 1 from current_words, else - from word's dictionary"

    stmt = (
        select(Word)
        .join(UserCurrentWord)
        .filter(UserCurrentWord.user_id == user_id)
        .order_by(func.random())  # ORDER BY RANDOM()
        .limit(1)
    )

    result = await session.execute(stmt)
    correct_word: Word = result.scalar()

    stmt = (
        select(Word)
        .where(Word.word_id != correct_word.word_id)
        .order_by(func.random())
        .limit(count)
    )

    result = await session.execute(stmt)
    variants = result.scalars().all()
    variants = cast(list[Word], variants)

    return dict(correct_word=correct_word,
                variants=variants)
