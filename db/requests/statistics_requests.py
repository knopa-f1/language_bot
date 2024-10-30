from db.models import ChatStatistic, Status
from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert
import logging

logger = logging.getLogger(__name__)


async def get_chat_statistic(
        session: AsyncSession,
        chat_id: int
) -> dict | None:
    default_status = Status.new
    learned_status = Status.learned

    stmt = (
        select(
            func.sum(ChatStatistic.correct + ChatStatistic.wrong).label("all"),
            func.sum(ChatStatistic.correct).label("correct"),
            case(
                (func.sum(ChatStatistic.correct + ChatStatistic.wrong) == 0, 0),
                else_=(func.sum(ChatStatistic.correct) * 100 / func.sum(ChatStatistic.correct + ChatStatistic.wrong))
            ).label("correct_percent"),
            func.sum(
                case(
                    (func.coalesce(ChatStatistic.status, default_status) == learned_status, 1),
                    else_=0
                )
            ).label("learned")
        )
        .filter(ChatStatistic.chat_id == chat_id)
    )

    result = await session.execute(stmt)
    row = result.first()
    return None if row[0] is None else row._asdict()


async def change_word_status(
        session: AsyncSession,
        chat_id: int,
        word_id: int,
        status: Status
):
    stmt = upsert(ChatStatistic).values(
        chat_id=chat_id,
        word_id=word_id,
        correct=0,
        wrong=0,
        status=status,
        status_date=func.now()
    ).on_conflict_do_update(
        index_elements=['chat_id', 'word_id'],
        set_={
            'status': status,
            'status_date': func.now()
        }
    )

    await session.execute(stmt)
    await session.commit()


async def should_del_current_word(
        session: AsyncSession,
        chat_id: int,
        word_id: int,
        count_correct: int,
        percent_correct: float
) -> bool:
    stmt = select(ChatStatistic).where(and_(ChatStatistic.chat_id == chat_id,
                                            ChatStatistic.word_id == word_id,
                                            ChatStatistic.correct >= count_correct,
                                            case(
                                                (ChatStatistic.correct + ChatStatistic.wrong == 0, 0),
                                                else_=(ChatStatistic.correct / (
                                                        ChatStatistic.correct + ChatStatistic.wrong))
                                            ) >= percent_correct
                                            ))
    result = await session.execute(stmt)
    row = result.fetchone()
    return row is not None


async def save_statistic_by_word(
        session: AsyncSession,
        chat_id: int,
        word_id: int,
        correct: int = 0,
        wrong: int = 0
) -> None:
    stmt = upsert(ChatStatistic).values(
        chat_id=chat_id,
        word_id=word_id,
        correct=correct,
        wrong=wrong,
        status=Status.in_progress,
        status_date=func.now()
    ).on_conflict_do_update(
        index_elements=['chat_id', 'word_id'],
        set_={
            'correct': ChatStatistic.correct + correct,
            'wrong': ChatStatistic.wrong + wrong,
            'status': Status.in_progress
        }
    )

    await session.execute(stmt)
    await session.commit()
