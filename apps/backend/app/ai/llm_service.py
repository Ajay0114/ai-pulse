from app.ai.providers.openrouter import OpenRouterProvider


class LLMService:
    def __init__(self):
        self.provider = OpenRouterProvider()

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are an AI research assistant.",
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str:
        return await self.provider.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )


llm_service = LLMService
