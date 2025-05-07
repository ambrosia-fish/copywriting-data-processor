import json
import logging
import os
from typing import Dict, List

from src.writers.base_writer import BaseWriter


class JsonWriter(BaseWriter):
    """Writes newsletter data to a JSON file."""
    
    def __init__(self, config: Dict):
        """Initialize the JSON writer.
        
        Args:
            config: Configuration dictionary for the JSON writer
        """
        self.output_path = config.get('path', 'data/newsletters.json')
    
    def write(self, newsletters: List[Dict]) -> None:
        """Write newsletter data to a JSON file.
        
        Args:
            newsletters: List of newsletter data dictionaries
        """
        logging.info(f"Writing {len(newsletters)} newsletters to JSON: {self.output_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Write to JSON
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(newsletters, f, indent=2, ensure_ascii=False)
        
        logging.info(f"Successfully wrote data to {self.output_path}")