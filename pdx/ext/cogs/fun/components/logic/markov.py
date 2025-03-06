import re
from collections import defaultdict

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _tokenize_sentence(
    sentence: str,
) -> list[str]:
    def find_special_entities(text: str) -> dict[tuple[int, int], tuple[str, str]]:
        entities = {}

        url_pattern = r"https?://\S+|www\.\S+"
        for match in re.finditer(url_pattern, text):
            start, end = match.span()
            entities[(start, end)] = ("URL", match.group())

        time_pattern = r"\b\d{1,2}[h:]\d{0,2}\b|\b\d{1,2}h\b"
        for match in re.finditer(time_pattern, text):
            start, end = match.span()
            if not any(s <= start < e or s < end <= e for s, e in entities.keys()):
                entities[(start, end)] = ("TIME", match.group())

        number_pattern = r"\b\d+[.,]\d+\b|\b\d+\b|R\$\s*\d+[.,]\d+"
        for match in re.finditer(number_pattern, text):
            start, end = match.span()
            if not any(s <= start < e or s < end <= e for s, e in entities.keys()):
                entities[(start, end)] = ("NUM", match.group())

        return entities

    def create_segments(
        text: str,
        entities: dict[tuple[int, int], tuple[str, str]],
    ) -> list[tuple[bool, str]]:
        segments = []
        last_end = 0

        for (start, end), (_, value) in sorted(entities.items()):
            if start > last_end:
                segments.append((False, text[last_end:start]))
            segments.append((True, value))
            last_end = end

        if last_end < len(text):
            segments.append((False, text[last_end:]))

        return segments

    def process_segment(
        is_special: bool,
        text: str,
    ) -> list[str]:
        if is_special:
            return [text]
        else:
            basic_pattern = r'(\s+|[.,!?;:"\'\(\)\[\]{}]|\b)'
            parts = re.split(basic_pattern, text)
            return [
                part.lower().strip()
                for part in parts
                if part and not part.isspace() and part.strip()
            ]

    def clean_token_list(token_list: list[str]) -> list[str]:
        cleaned = []
        prev_token = None
        for token in token_list:
            if token and not token.isspace() and token != prev_token:
                cleaned.append(token)
                prev_token = token
        return cleaned

    tokens = []

    if not sentence:
        return []

    special_entities = find_special_entities(sentence)
    segments = create_segments(sentence, special_entities)

    for is_special, text in segments:
        tokens.extend(process_segment(is_special, text))

    final_tokens = clean_token_list(tokens)

    return final_tokens


async def process_message(sentence: str, session: AsyncSession) -> None:
    words = ["<s>"] + _tokenize_sentence(sentence) + ["</s>"]

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
