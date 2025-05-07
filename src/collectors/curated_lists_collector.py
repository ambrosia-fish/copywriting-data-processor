import logging
import re
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class CuratedListsCollector(BaseCollector):
    """Collects newsletter data from curated lists."""
    
    def __init__(self, config: Dict):
        """Initialize the curated lists collector.
        
        Args:
            config: Configuration dictionary for the curated lists collector
        """
        self.sources = config.get('sources', [])
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from curated lists.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        for url in self.sources:
            try:
                logging.info(f"Collecting from curated list: {url}")
                response = requests.get(
                    url, 
                    headers={'User-Agent': self.user_agent}, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Look for elements that likely contain newsletter information
                    found_items = self._extract_newsletter_items(soup, url)
                    
                    logging.info(f"Found {len(found_items)} newsletter items in {url}")
                    newsletters.extend(found_items)
                else:
                    logging.error(f"Failed to fetch curated list {url}, status code: {response.status_code}")
            except Exception as e:
                logging.error(f"Error collecting from curated list {url}: {str(e)}")
        
        return newsletters
    
    def _extract_newsletter_items(self, soup: BeautifulSoup, source_url: str) -> List[Dict]:
        """Extract newsletter information from the HTML soup.
        
        Args:
            soup: BeautifulSoup object of the curated list page
            source_url: URL of the curated list
        
        Returns:
            List of newsletter data dictionaries
        """
        items = []
        
        # Different sites have different structures, try different strategies
        
        # Strategy 1: Look for headings (h2, h3, etc.) that might contain newsletter names
        headings = soup.find_all(['h2', 'h3', 'h4'])
        for heading in headings:
            # Check if heading contains relevant keywords
            if any(kw in heading.text.lower() for kw in ['newsletter', 'copywriting', 'marketing']):
                # Look for links near the heading
                link_elem = heading.find('a') or heading.find_next('a')
                if link_elem and 'href' in link_elem.attrs:
                    link = link_elem['href']
                    # Make sure link is absolute
                    if link.startswith('/'):
                        link = '/'.join(source_url.split('/')[:3]) + link
                    
                    # Extract publisher if available
                    publisher_elem = heading.find_next(['p', 'div'])
                    publisher = ''
                    if publisher_elem:
                        # Look for text that might contain author/publisher info
                        publisher_text = publisher_elem.text
                        # Try to extract author/publisher name using regex patterns
                        author_match = re.search(r'by\s+([\w\s]+)', publisher_text, re.IGNORECASE)
                        if author_match:
                            publisher = author_match.group(1).strip()
                    
                    items.append({
                        'name': heading.text.strip(),
                        'link': link,
                        'publisher': publisher,
                        'email': '',  # Usually not available in curated lists
                        'subscribers': None,  # Usually not available in curated lists
                        'social_media': {},  # Usually not available in curated lists
                        'source': 'curated_list'
                    })
        
        # Strategy 2: Look for list items that might contain newsletter info
        list_items = soup.find_all('li')
        for item in list_items:
            link_elem = item.find('a')
            if link_elem and 'href' in link_elem.attrs:
                link = link_elem['href']
                # Check if link is to a newsletter or relevant site
                if any(domain in link for domain in ['substack.com', 'beehiiv.com', 'convertkit.com', 'newsletter']):
                    # Make sure link is absolute
                    if link.startswith('/'):
                        link = '/'.join(source_url.split('/')[:3]) + link
                    
                    items.append({
                        'name': link_elem.text.strip(),
                        'link': link,
                        'publisher': '',  # Usually not available in this format
                        'email': '',  # Usually not available in curated lists
                        'subscribers': None,  # Usually not available in curated lists
                        'social_media': {},  # Usually not available in curated lists
                        'source': 'curated_list'
                    })
        
        return items