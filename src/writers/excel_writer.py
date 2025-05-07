import logging
import os
from typing import Dict, List

import pandas as pd

from src.writers.base_writer import BaseWriter


class ExcelWriter(BaseWriter):
    """Writes newsletter data to an Excel file."""
    
    def __init__(self, config: Dict):
        """Initialize the Excel writer.
        
        Args:
            config: Configuration dictionary for the Excel writer
        """
        self.output_path = config.get('path', 'data/newsletters.xlsx')
    
    def write(self, newsletters: List[Dict]) -> None:
        """Write newsletter data to an Excel file.
        
        Args:
            newsletters: List of newsletter data dictionaries
        """
        logging.info(f"Writing {len(newsletters)} newsletters to Excel: {self.output_path}")
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        # Process the data for Excel
        processed_data = []
        for newsletter in newsletters:
            # Convert social_media dict to string
            social_media = newsletter.get('social_media', {})
            social_media_str = ' | '.join([f"{platform}: {url}" for platform, url in social_media.items()])
            
            # Create row with processed social_media
            row = {
                'Name': newsletter.get('name', ''),
                'Link': newsletter.get('link', ''),
                'Publisher': newsletter.get('publisher', ''),
                'Email': newsletter.get('email', ''),
                'Subscribers': newsletter.get('subscribers', ''),
                'Social Media': social_media_str,
                'Source': newsletter.get('source', '')
            }
            
            processed_data.append(row)
        
        # Convert to DataFrame
        df = pd.DataFrame(processed_data)
        
        # Write to Excel
        df.to_excel(self.output_path, index=False, engine='openpyxl')
        
        logging.info(f"Successfully wrote data to {self.output_path}")