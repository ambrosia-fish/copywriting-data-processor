"""
Filter strategies for newsletter data.

This module contains strategies for filtering newsletter data based on completeness and quality.
"""

from typing import Dict, List


class CompleteDataFilterStrategy:
    """Filter strategy that only keeps newsletters with complete data."""
    
    def __init__(self, required_fields=None):
        """Initialize the filter strategy.
        
        Args:
            required_fields: List of required fields
        """
        self.required_fields = required_fields or [
            'name', 
            'link', 
            'publisher', 
            'email', 
            'subscribers'
        ]
    
    def filter(self, newsletters: List[Dict]) -> List[Dict]:
        """Filter newsletters to only keep those with complete data.
        
        Args:
            newsletters: List of newsletter data dictionaries
        
        Returns:
            Filtered list of newsletter data dictionaries
        """
        filtered_newsletters = []
        
        for newsletter in newsletters:
            # Check if all required fields are present and not empty
            if all(newsletter.get(field) for field in self.required_fields):
                filtered_newsletters.append(newsletter)
        
        return filtered_newsletters
