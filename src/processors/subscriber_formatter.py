import logging
from typing import Dict, List, Optional, Union


class SubscriberFormatter:
    """Formats subscriber counts according to requirements."""
    
    def __init__(self, config: Dict):
        """Initialize the subscriber formatter.
        
        Args:
            config: Configuration dictionary for the subscriber formatter
        """
        self.config = config
        self.default_if_unknown = config.get('default_if_unknown', False)
        self.default_value = config.get('default_value', 1000)
        self.rounding = config.get('rounding', {
            'less_than_1000': 100,
            'less_than_10000': 1000,
            'less_than_500000': 10000,
            'above_500000': 100000,
            'million_plus': '1 Million+'
        })
    
    def process(self, newsletters: List[Dict]) -> List[Dict]:
        """Format subscriber counts in newsletter data.
        
        Args:
            newsletters: List of newsletter data dictionaries
        
        Returns:
            List of newsletter data dictionaries with formatted subscriber counts
        """
        logging.info(f"Formatting subscriber counts for {len(newsletters)} newsletters")
        
        for newsletter in newsletters:
            subscribers = newsletter.get('subscribers')
            
            # Format the subscriber count
            formatted_subscribers = self._format_subscriber_count(subscribers)
            
            # Update the newsletter data
            newsletter['subscribers'] = formatted_subscribers
        
        return newsletters
    
    def _format_subscriber_count(self, count: Optional[Union[int, str]]) -> str:
        """Format subscriber count according to requirements.
        
        Args:
            count: Raw subscriber count
        
        Returns:
            Formatted subscriber count
        """
        if count is None:
            if self.default_if_unknown:
                return str(self.default_value)
            return ''
        
        try:
            # Convert to integer if it's a string
            if isinstance(count, str):
                # Remove commas and other non-numeric characters
                count = ''.join(c for c in count if c.isdigit())
                count = int(count) if count else 0
            
            # Apply rounding rules
            if count >= 1000000:
                return self.rounding.get('million_plus', '1 Million+')
            elif count >= 500000:
                return str(round(count / self.rounding.get('above_500000', 100000)) * self.rounding.get('above_500000', 100000))
            elif count >= 10000:
                return str(round(count / self.rounding.get('less_than_500000', 10000)) * self.rounding.get('less_than_500000', 10000))
            elif count >= 1000:
                return str(round(count / self.rounding.get('less_than_10000', 1000)) * self.rounding.get('less_than_10000', 1000))
            else:
                return str(round(count / self.rounding.get('less_than_1000', 100)) * self.rounding.get('less_than_1000', 100))
        except (ValueError, TypeError):
            if self.default_if_unknown:
                return str(self.default_value)
            return ''