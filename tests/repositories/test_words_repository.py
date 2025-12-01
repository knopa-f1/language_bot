import pytest
from sqlalchemy import select

from db.models import Word, ChatCurrentWord


class TestWordsRepository:

    @pytest.mark.asyncio
    async def test_get_word_by_id(self, words_repo, session):
        w = Word(word_id=1, word="cat", translation_ru="кот", type="n")
        session.add(w)
        await session.commit()

        found = await words_repo.get_word_by_id(1)
        assert found.word == "cat"

    @pytest.mark.asyncio
    async def test_add_current_chat_words(self, words_repo, session):
        # prepare 3 words
        for i in range(1, 4):
            session.add(Word(word_id=i, word=f"w{i}", translation_ru=f"t{i}", type="n"))
        await session.commit()

        # add one
        await words_repo.add_current_chat_words(10, interval_days=3, count=1)

        q = await session.execute(select(ChatCurrentWord))
        rows = q.scalars().all()
        assert len(rows) == 1
        assert rows[0].chat_id == 10

    @pytest.mark.asyncio
    async def test_delete_current_word(self, words_repo, session):
        session.add(ChatCurrentWord(chat_id=10, word_id=1))
        await session.commit()

        await words_repo.delete_current_word(10, 1)
        await session.commit()

        q = await session.execute(select(ChatCurrentWord))
        assert q.scalars().first() is None

    @pytest.mark.asyncio
    async def test_delete_random_current_words(self, words_repo, session):
        for i in range(1, 4):
            session.add(ChatCurrentWord(chat_id=10, word_id=i))
        await session.commit()

        await words_repo.delete_random_current_words(10, 2)

        q = await session.execute(select(ChatCurrentWord))
        rows = q.scalars().all()
        assert len(rows) == 1

    @pytest.mark.asyncio
    async def test_current_words_exists(self, words_repo, session):
        session.add(ChatCurrentWord(chat_id=10, word_id=1))
        await session.commit()

        assert await words_repo.current_words_exists(10) is True
        assert await words_repo.current_words_exists(99) is False

    @pytest.mark.asyncio
    async def test_exists_short_word(self, words_repo, session):
        session.add(Word(word_id=1, word="hi", translation_ru="пр", type="n"))
        session.add(ChatCurrentWord(chat_id=10, word_id=1))
        await session.commit()

        exists = await words_repo.exists_short_word(10, max_len=3)
        assert exists is True

    @pytest.mark.asyncio
    async def test_get_words(self, words_repo, session):
        # prepare
        session.add(Word(word_id=1, word="cat", translation_ru="кот", type="n"))
        session.add(Word(word_id=2, word="dog", translation_ru="пёс", type="n"))
        session.add(ChatCurrentWord(chat_id=10, word_id=1))
        await session.commit()

        result = await words_repo.get_words(10, count=1)
        assert "correct_word" in result
        assert "variants" in result
        assert isinstance(result["variants"], list)
