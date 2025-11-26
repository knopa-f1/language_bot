import datetime
import logging

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChatStatistic, Status
from db.models.statistics import ChatActivityStatistic
from db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class StatisticsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def get_chat_statistic(self, chat_id: int) -> dict | None:
        default_status = Status.new
        learned_status = Status.learned
        already_know_status = Status.already_know

        stmt = select(
            func.sum(ChatStatistic.correct + ChatStatistic.wrong).label("all"),
            func.sum(ChatStatistic.correct).label("correct"),
            case(
                (func.sum(ChatStatistic.correct + ChatStatistic.wrong) == 0, 0),
                else_=(func.sum(ChatStatistic.correct) * 100 / func.sum(ChatStatistic.correct + ChatStatistic.wrong)),
            ).label("correct_percent"),
            func.sum(
                case(
                    (
                        or_(
                            func.coalesce(ChatStatistic.status, default_status) == learned_status,
                            func.coalesce(ChatStatistic.status, default_status) == already_know_status,
                        ),
                        1,
                    ),
                    else_=0,
                )
            ).label("learned"),
        ).filter(ChatStatistic.chat_id == chat_id)

        result = await self.session.execute(stmt)
        row = result.first()
        return None if row[0] is None else row._asdict()

    async def change_word_status(self, chat_id: int, word_id: int, status: str):
        stmt = (
            upsert(ChatStatistic)
            .values(
                chat_id=chat_id,
                word_id=word_id,
                correct=0,
                wrong=0,
                status=status,
                status_date=func.now(),
            )
            .on_conflict_do_update(
                index_elements=["chat_id", "word_id"],
                set_={"status": status, "status_date": func.now()},
            )
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def should_del_current_word(
        self,
        chat_id: int,
        word_id: int,
        count_correct: int,
        percent_correct: float,
    ) -> bool:
        stmt = select(ChatStatistic).where(
            and_(
                ChatStatistic.chat_id == chat_id,
                ChatStatistic.word_id == word_id,
                ChatStatistic.correct >= count_correct,
                case(
                    (ChatStatistic.correct + ChatStatistic.wrong == 0, 0),
                    else_=(ChatStatistic.correct / (ChatStatistic.correct + ChatStatistic.wrong)),
                )
                >= percent_correct,
            )
        )
        result = await self.session.execute(stmt)
        row = result.fetchone()
        return row is not None

    async def save_statistic_by_word(self, chat_id: int, word_id: int, correct: int = 0, wrong: int = 0) -> None:
        stmt = (
            upsert(ChatStatistic)
            .values(
                chat_id=chat_id,
                word_id=word_id,
                correct=correct,
                wrong=wrong,
                status=Status.in_progress,
                status_date=func.now(),
            )
            .on_conflict_do_update(
                index_elements=["chat_id", "word_id"],
                set_={
                    "correct": ChatStatistic.correct + correct,
                    "wrong": ChatStatistic.wrong + wrong,
                    "status": Status.in_progress,
                },
            )
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def upsert_chat_event_stat(self, chat_id: int, date: datetime.date) -> None:
        stmt = upsert(ChatActivityStatistic).values(chat_id=chat_id, date=date, event_count=1)
        stmt = stmt.on_conflict_do_update(
            index_elements=["chat_id", "date"],
            set_={"event_count": ChatActivityStatistic.event_count + 1},
        )

        await self.session.execute(stmt)
        await self.session.commit()
