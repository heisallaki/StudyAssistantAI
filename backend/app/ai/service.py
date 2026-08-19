from app.ai.prompts.tutor_prompts import build_system_prompt
from app.ai.providers.base import AIProvider


class AITutorService:
    def __init__(self, provider: AIProvider):
        self.provider = provider

    async def generate_reply(
        self,
        history: list[dict[str, str]],
        explanation_level: str,
        mode: str,
        subject_context: str | None,
    ) -> str:
        system_prompt = build_system_prompt(explanation_level, mode, subject_context)
        messages = [{"role": "system", "content": system_prompt}, *history]
        return await self.provider.generate_reply(messages)