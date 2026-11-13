import httpx

from app.core.config import settings


class OpenRouterError(Exception):
    pass


class OpenRouterProvider:
    def __init__(self):
        if not settings.OPENROUTER_API_KEY:
            raise OpenRouterError("OpenRouter API key is not configured.")

        self.base_url = settings.OPENROUTER_BASE_URL.rstrip("/")
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.LLM_MODEL

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "You are an AI research assistant.",
        temperature: float = 0.2,
        max_tokens: int = 1000,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Pulse",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                )

            if response.is_error:
                raise OpenRouterError(
                    f"OpenRouter returned HTTP {response.status_code}: "
                    f"{response.text[:1000]}"
                )

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            if not isinstance(content, str) or not content.strip():
                raise OpenRouterError("OpenRouter returned an empty response.")

            return content.strip()

        except httpx.TimeoutException as exc:
            raise OpenRouterError("OpenRouter request timed out.") from exc
        except httpx.RequestError as exc:
            raise OpenRouterError(f"OpenRouter connection failed: {exc}") from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterError("Unexpected OpenRouter response format.") from exc
    

    async def embed(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise OpenRouterError("Embedding input cannot be empty.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "AI Pulse",
        }

        payload = {
            "model": settings.EMBEDDING_MODEL,
            "input": text.strip()[:12000],
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/embeddings",
                    headers=headers,
                    json=payload,
                )

            if response.is_error:
                raise OpenRouterError(
                    f"OpenRouter embedding error HTTP {response.status_code}: "
                    f"{response.text[:1000]}"
                )

            data = response.json()
            embedding = data["data"][0]["embedding"]

            if not isinstance(embedding, list) or len(embedding) != 1536:
                raise OpenRouterError(
                    f"Expected 1536 embedding dimensions, "
                    f"received {len(embedding) if isinstance(embedding, list) else 'invalid response'}."
                )

            return embedding

        except httpx.TimeoutException as exc:
            raise OpenRouterError("Embedding request timed out.") from exc
        except httpx.RequestError as exc:
            raise OpenRouterError(
                f"Embedding connection failed: {exc}"
            ) from exc
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise OpenRouterError(
                "Unexpected embedding response format."
            ) from exc

