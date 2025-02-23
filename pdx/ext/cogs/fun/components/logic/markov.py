import re
from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def process_message(sentence: str, session: AsyncSession) -> None:
    words = (
        ["<s>"]
        + [
            token.strip()
            for token in re.split(r"(\w+[.,!?;]?|\s+)", sentence.lower())
            if token and not token.isspace()
        ]
        + ["</s>"]
    )

    if len(words) < 3:
        return

    if len(words) > 100:
        words = words[:100] + ["</s>"]

    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(words) - 1):
        current_state = words[i][:50]
        next_state = words[i + 1][:50]
        transitions[current_state][next_state] += 1

    try:
        values = [
            {"current_state": curr, "next_state": next_, "count": count}
            for curr, nexts in transitions.items()
            for next_, count in nexts.items()
        ]

        if values:
            stmt = text("""
                INSERT INTO markov_transitions (current_state, next_state, count)
                VALUES (:current_state, :next_state, :count)
                ON CONFLICT (current_state, next_state) DO UPDATE
                SET count = markov_transitions.count + EXCLUDED.count
            """)
            await session.execute(stmt, values)
            await session.commit()

    except Exception as e:
        await session.rollback()
        raise RuntimeError(f"Falha ao processar mensagem: {e}") from e
