from models.character import Character
def build_character_system_prompt(ch: Character) -> str:
    interests = ", ".join(ch.interests or [])
    return (
        "Ты отвечаешь от лица нижеописанного персонажа. Отвечай в его стиле, "
        "сохраняй характер и знания. Избегай противоречий:\n\n"
        f"Профиль персонажа:\n"
        f"- Имя: {ch.name}\n"
        f"- Пол: {ch.gender or 'не указан'}\n"
        f"- Bio: {ch.bio or '—'}\n"
        f"- Интересы: {interests or '—'}\n\n"
        f"Контекст/обстановка:\n{ch.context}"
    )