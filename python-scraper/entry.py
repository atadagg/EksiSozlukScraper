from dataclasses import dataclass

@dataclass
class Entry:
    id: str
    author: str
    timestamp: str
    content: str
    scraped_at: str 