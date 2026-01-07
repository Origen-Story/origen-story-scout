from ..llm.router import LLMRouter, TaskType
from ..sources.base import ContentItem
from typing import List

class Summarizer:
    def __init__(self):
        self.router = LLMRouter()

    def summarize_item(self, item: ContentItem) -> str:
        system_prompt = (
            "You are a professional content curator. Summarize the following article content into 2-3 concise bullet points. "
            "Focus on the 'why it matters' and key facts. Keep it professional and objective."
        )
        # Truncate content to avoid hitting TPM limit on free tier
        truncated_content = item.content[:2000] if item.content else "No content available."
        prompt = f"Title: {item.title}\nSource: {item.source_name}\n\nContent:\n{truncated_content}"
        
        try:
            import time
            time.sleep(5) # Rate limiting for free tier
            # We use general task for basic summarization
            summary = self.router.generate(prompt, task=TaskType.GENERAL, system_prompt=system_prompt)
            return summary
        except Exception as e:
            print(f"Warning: Failed to summarize '{item.title}': {e}")
            return "Summary unavailable."

    def process_batch(self, items: List[ContentItem]):
        for item in items:
            item.summary = self.summarize_item(item)
