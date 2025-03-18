import random
from collections import defaultdict
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

nlp = spacy.load("pt_core_news_sm")


def tokenize(text: str) -> list[str]:
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_punct and not token.is_space]
    return tokens


async def process_message(
        sentence: str,
        session: AsyncSession,
) -> None:
    words = tokenize(sentence)

    if len(words) <= 1:
        return

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


async def mark_prohibited_state(
        state: str,
        session: AsyncSession,
) -> None:
    try:
        stmt = text("""
            INSERT INTO prohibited_states (state)
            VALUES (:state)
            ON CONFLICT (state) DO NOTHING
        """)
        await session.execute(stmt, {"state": state})
        await session.commit()

    except Exception as e:
        await session.rollback()
        raise RuntimeError(f"Falha ao marcar estado proibido: {e}") from e


async def get_prohibited_states(
        session: AsyncSession,
) -> list[str]:
    stmt = text("SELECT state FROM prohibited_states")
    result = await session.execute(stmt)
    return [row[0] for row in result]


async def generate_chain(
    session: AsyncSession,
    start_token: str = None,
    length: int = 100,
    temperature: float = 1.2,
    diversity_factor: float = 0.85,
    max_repetition: int = 3,
    min_transitions: int = 10
) -> str:
    prohibited_states = set(await get_prohibited_states(session))

    if not start_token:
        start_query = text("""
            SELECT current_state FROM markov_transitions
            WHERE current_state NOT IN (SELECT state FROM prohibited_states)
            GROUP BY current_state
            ORDER BY random()
            LIMIT 1
        """)
        result = await session.execute(start_query)
        row = result.first()
        start_token = row[0] if row else None

        if not start_token:
            return ""

    chain = [start_token]
    current_token = start_token
    token_usage: dict[str, float] = {start_token: 1.0}
    consecutive_repeats = 0

    for _ in range(length - 1):
        next_query = text("""
            SELECT next_state, count 
            FROM markov_transitions 
            WHERE current_state = :current_state
        """)
        result = await session.execute(next_query, {"current_state": current_token})
        transitions = [(row[0], row[1]) for row in result
                      if row[0] not in prohibited_states]

        if not transitions:
            recovery_query = text("""
                SELECT current_state FROM markov_transitions
                WHERE current_state NOT IN (SELECT state FROM prohibited_states)
                GROUP BY current_state
                HAVING COUNT(DISTINCT next_state) > :min_transitions
                ORDER BY random()
                LIMIT 1
            """)
            recovery_result = await session.execute(recovery_query,
                                                   {"min_transitions": min_transitions})
            recovery_row = recovery_result.first()
            if not recovery_row:
                break

            current_token = recovery_row[0]
            chain.append(current_token)
            token_usage[current_token] = token_usage.get(current_token, 0) + 1.0
            continue

        weights = []
        for state, count in transitions:
            weight = count ** (1 / max(0.1, temperature))

            usage_penalty = token_usage.get(state, 0)
            if usage_penalty > 0:
                weight *= (diversity_factor ** usage_penalty)

            weights.append((state, weight))

        total = sum(w for _, w in weights)
        if total <= 0:
            next_token = random.choice([s for s, _ in transitions])
        else:
            states, probs = zip(*[(s, w/total) for s, w in weights])
            next_token = random.choices(states, weights=probs, k=1)[0]

        if next_token == current_token:
            consecutive_repeats += 1
            if consecutive_repeats >= max_repetition:
                alternatives = [(s, w) for s, w in weights if s != current_token]
                if alternatives:
                    alt_states, alt_weights = zip(*alternatives)
                    next_token = random.choices(alt_states, weights=alt_weights, k=1)[0]
                    consecutive_repeats = 0
        else:
            consecutive_repeats = 0

        chain.append(next_token)
        current_token = next_token

        token_usage[next_token] = token_usage.get(next_token, 0) + 1.0

        for token in list(token_usage.keys()):
            token_usage[token] *= 0.95
            if token_usage[token] < 0.05 and token != next_token:
                del token_usage[token]

    return " ".join(chain)
