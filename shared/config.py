import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Topic(BaseModel):
    name: str
    keywords: List[str]
    weight: float = 1.0

class UserPreferences(BaseModel):
    time_window_days: int = 10
    min_relevance_score: float = 0.3
    max_items_per_run: int = 20
    highlight_trending: bool = True
    highlight_unique: bool = True
    auto_summarize: bool = False  # Automatically generate summaries (uses API tokens)
    summary_count: int = 9  # Number of top stories to summarize

class InterestConfig(BaseModel):
    topics: List[Topic]
    preferences: UserPreferences

class RSSFeed(BaseModel):
    name: str
    url: str
    category: str = "general"

class GmailConfig(BaseModel):
    enabled: bool = False
    label_name: str = "Newsletters"
    credentials_path: str = "config/credentials.json"

class SourceConfig(BaseModel):
    opml_file: Optional[str] = None
    rss_feeds: List[RSSFeed] = []
    newsletter_directory: str = "data/newsletters"
    newsletter_formats: List[str] = [".eml", ".html", ".txt"]
    gmail: GmailConfig = GmailConfig()

class Config:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.interests = self._load_interests()
        self.sources = self._load_sources()
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

    def _load_interests(self) -> InterestConfig:
        path = self.config_dir / "interests.yaml"
        # Fallback to example if real one doesn't exist (for fresh clones)
        if not path.exists():
            path = self.config_dir / "interests.example.yaml"
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return InterestConfig(**data)

    def _load_sources(self) -> SourceConfig:
        path = self.config_dir / "sources.yaml"
        if not path.exists():
            path = self.config_dir / "sources.example.yaml"
            
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return SourceConfig(**data)

# Singleton instance
settings = Config()
