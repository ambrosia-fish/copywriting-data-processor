from abc import ABC, abstractmethod
from typing import Dict, List


class BaseWriter(ABC):
    """Base class for all data writers."""
    
    @abstractmethod
    def write(self, newsletters: List[Dict]) -> None:
        """Write newsletter data to output.
        
        Args:
            newsletters: List of newsletter data dictionaries
        """
        pass