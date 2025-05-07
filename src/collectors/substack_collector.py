import logging
import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class SubstackCollector(BaseCollector):
    """Collects newsletter data from Substack."""
    
    def __init__(self, config: Dict):
        """Initialize the Substack collector.
        
        Args:
            config: Configuration dictionary for the Substack collector
        """
        self.keywords = config.get('keywords', ['copywriting', 'marketing'])
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from Substack.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        for keyword in self.keywords:
            try:
                # Search Substack for the keyword
                search_url = f"https://substack.com/search?query={keyword}&offset=0&sort=top"
                logging.info(f"Searching Substack for keyword: {keyword}")
                
                response = requests.get(
                    search_url, 
                    headers={'User-Agent': self.user_agent}, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find publication cards
                    publication_cards = soup.select('div.publication-card')
                    
                    for card in publication_cards:
                        try:
                            # Extract name and link
                            name_elem = card.select_one('h3')
                            if not name_elem:
                                continue
                            
                            name = name_elem.text.strip()
                            
                            link_elem = card.select_one('a.publication-title')
                            if not link_elem or 'href' not in link_elem.attrs:
                                continue
                            
                            link = link_elem['href']
                            # Make sure link is absolute
                            if not link.startswith('http'):
                                link = 'https://substack.com' + link
                            
                            # Extract publisher
                            publisher_elem = card.select_one('div.publisher-name')
                            publisher = publisher_elem.text.strip() if publisher_elem else ''
                            
                            # Extract subscriber count if available
                            subscribers = None
                            subscribers_elem = card.select_one('div.subscription-count')
                            if subscribers_elem:
                                subscriber_text = subscribers_elem.text.strip()
                                # Extract number from text like "1,234 subscribers"
                                match = re.search(r'([\d,]+)', subscriber_text)
                                if match:
                                    try:
                                        subscribers = int(match.group(1).replace(',', ''))
                                    except ValueError:
                                        pass
                            
                            # Add to newsletters
                            newsletters.append({
                                'name': name,
                                'link': link,
                                'publisher': publisher,
                                'email': '',  # Usually not directly available on search page
                                'subscribers': subscribers,
                                'social_media': {},  # Usually not directly available on search page
                                'source': 'substack'
                            })
                        except Exception as e:
                            logging.error(f"Error parsing Substack publication card: {str(e)}")
                else:
                    logging.error(f"Failed to search Substack for {keyword}, status code: {response.status_code}")
            except Exception as e:
                logging.error(f"Error searching Substack for {keyword}: {str(e)}")
        
        return newsletters