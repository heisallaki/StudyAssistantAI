import json

from pydantic import BaseModel, Field


class GeneratedFlashcard(BaseModel):
    front: str
    back: str


class GeneratedFlashcardSet(BaseModel):
    flashcards: list[GeneratedFlashcard] = Field(default_factory=list)


def _is_flashcard_valid(card: GeneratedFlashcard) -> bool:
    return bool(card.front.strip()) and bool(card.back.strip())


def parse_generated_flashcards(raw_text: str) -> list[GeneratedFlashcard]:
    data = json.loads(raw_text)
    parsed = GeneratedFlashcardSet.model_validate(data)
    return [card for card in parsed.flashcards if _is_flashcard_valid(card)]