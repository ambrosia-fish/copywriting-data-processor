from abc import ABC, abstractmethod
from typing import Dict, List


class BaseCollector(ABC):
    """Base class for all data collectors."""
    
    @abstractmethod
    def collect(self) -> List[Dict]:
        """Collect newsletter data.
        
        Returns:
            List[Dict]: List of newsletter data dictionaries with keys:
                - name: Name of the newsletter
                - link: Direct link to the newsletter
                - publisher: Owner/publisher name
                - email: Contact email address
                - subscribers: Subscriber count (when available)
                - social_media: Dict of social media accounts
        """
        pass