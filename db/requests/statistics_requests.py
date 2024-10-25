from db.models import UsersStatistic, Status
from sqlalchemy import select, and_, func, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert
import logging

logger = logging.getLogger(__name__)


async def get_user_statistic(
        session: AsyncSession,
        user_id: int
) -> dict | None:
    default_status = Status.new
    learned_status = Status.learned

    stmt = (
        select(
            func.sum(UsersStatistic.correct + UsersStatistic.wrong).label("all"),
            func.sum(UsersStatistic.correct).label("correct"),
            case(
                (func.sum(UsersStatistic.correct + UsersStatistic.wrong) == 0, 0),
                else_=(func.sum(UsersStatistic.correct) * 100 / func.sum(UsersStatistic.correct + UsersStatistic.wrong))
            ).label("correct_percent"),
            func.sum(
                case(
                    (func.coalesce(UsersStatistic.status, default_status) == learned_status, 1),
                    else_=0
                )
            ).label("learned")
        )
        .filter(UsersStatistic.user_id == user_id)
    )

    result = await session.execute(stmt)
    row = result.first()
    return None if row is None else row._asdict()


async def change_word_status(
        session: AsyncSession,
        user_id: int,
        word_id: int,
        status: Status
):
    stmt = upsert(UsersStatistic).values(
        user_id=user_id,
        word_id=word_id,
        correct=0,
        wrong=0,
        status=status,
        status_date=func.now()
    ).on_conflict_do_update(
        index_elements=['user_id', 'word_id'],
        set_={
            'status': status,
            'status_date': func.now()
        }
    )

    await session.execute(stmt)
    await session.commit()


async def should_del_current_word(
        session: AsyncSession,
        user_id: int,
        word_id: int,
        count_correct: int,
        percent_correct: float
) -> bool:
    stmt = select(UsersStatistic).where(and_(UsersStatistic.user_id == user_id,
                                             UsersStatistic.word_id == word_id,
                                             UsersStatistic.correct >= count_correct,
                                             case(
                                                 (UsersStatistic.correct + UsersStatistic.wrong == 0, 0),
                                                 else_=(UsersStatistic.correct / (
                                                         UsersStatistic.correct + UsersStatistic.wrong))
                                             ) >= percent_correct
                                             ))
    result = await session.execute(stmt)
    row = result.fetchone()
    print("should_del_current_word", word_id, row)
    return row is not None


async def save_statistic_by_word(
        session: AsyncSession,
        user_id: int,
        word_id: int,
        correct: int = 0,
        wrong: int = 0
) -> None:
    stmt = upsert(UsersStatistic).values(
        user_id=user_id,
        word_id=word_id,
        correct=correct,
        wrong=wrong,
        status=Status.in_progress,
        status_date=func.now()
    ).on_conflict_do_update(
        index_elements=['user_id', 'word_id'],
        set_={
            'correct': UsersStatistic.correct + correct,
            'wrong': UsersStatistic.wrong + wrong,
            'status': Status.in_progress
        }
    )

    await session.execute(stmt)
    await session.commit()
