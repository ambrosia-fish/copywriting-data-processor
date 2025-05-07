import csv
import logging
import os
from typing import Dict, List

from src.writers.base_writer import BaseWriter


class CsvWriter(BaseWriter):
    """Writes newsletter data to a CSV file."""
    
    def __init__(self, config: Dict):
        """Initialize the CSV writer.
        
        Args:
            config: Configuration dictionary for the CSV writer
        """
        self.output_path = config.get('path', 'newsletters.csv')
    
    def write(self, newsletters: List[Dict]) -> None:
        """Write newsletter data to a CSV file.
        
        Args:
            newsletters: List of newsletter data dictionaries
        """
        logging.info(f"Writing {len(newsletters)} newsletters to CSV: {self.output_path}")
        
        # Ensure directory exists if there's a directory in the path
        output_dir = os.path.dirname(self.output_path)
        if output_dir:  # Only create directory if there's a directory path
            os.makedirs(output_dir, exist_ok=True)
        
        # Define column headers
        fieldnames = ['name', 'link', 'publisher', 'email', 'subscribers', 'social_media', 'source']
        
        # Write to CSV
        with open(self.output_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for newsletter in newsletters:
                # Convert social_media dict to string
                social_media = newsletter.get('social_media', {})
                social_media_str = ' | '.join([f"{platform}: {url}" for platform, url in social_media.items()])
                
                # Create row with processed social_media
                row = {
                    'name': newsletter.get('name', ''),
                    'link': newsletter.get('link', ''),
                    'publisher': newsletter.get('publisher', ''),
                    'email': newsletter.get('email', ''),
                    'subscribers': newsletter.get('subscribers', ''),
                    'social_media': social_media_str,
                    'source': newsletter.get('source', '')
                }
                
                writer.writerow(row)
        
        logging.info(f"Successfully wrote data to {self.output_path}")
