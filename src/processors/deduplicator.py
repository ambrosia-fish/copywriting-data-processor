import logging
from typing import Dict, List

import pandas as pd


class Deduplicator:
    """Deduplicates newsletter data."""
    
    def process(self, newsletters: List[Dict]) -> List[Dict]:
        """Deduplicate newsletter data.
        
        Args:
            newsletters: List of newsletter data dictionaries
        
        Returns:
            Deduplicated list of newsletter data dictionaries
        """
        logging.info(f"Deduplicating {len(newsletters)} newsletters")
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(newsletters)
        
        # If there are no newsletters, return empty list
        if df.empty:
            return []
        
        # Count before deduplication
        initial_count = len(df)
        
        # Deduplicate based on link (exact matches)
        if 'link' in df.columns:
            df = df.drop_duplicates(subset=['link'], keep='first')
        
        # Deduplicate based on name (fuzzy matches)
        if 'name' in df.columns:
            # Clean name field
            df['name_clean'] = df['name'].str.lower().str.strip()
            
            # Sort by source priority (gives preference to certain sources)
            source_priority = {
                'rss': 3,
                'substack': 2,
                'feedspot': 1,
                'curated_list': 0
            }
            
            # Add source priority column
            df['source_priority'] = df['source'].map(source_priority)
            
            # Sort by source priority (higher = better)
            df = df.sort_values('source_priority', ascending=False)
            
            # Drop duplicates based on cleaned name
            df = df.drop_duplicates(subset=['name_clean'], keep='first')
            
            # Drop the temporary columns
            df = df.drop(['name_clean', 'source_priority'], axis=1)
        
        # Count after deduplication
        final_count = len(df)
        
        logging.info(f"Removed {initial_count - final_count} duplicate newsletters")
        
        # Convert back to list of dictionaries
        return df.to_dict('records')