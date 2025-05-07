import logging
import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class SubstackApiCollector(BaseCollector):
    """Collects newsletter data from Substack using web scraping."""
    
    def __init__(self, config: Dict):
        """Initialize the Substack collector.
        
        Args:
            config: Configuration dictionary for the Substack collector
        """
        self.keywords = config.get('keywords', ['copywriting', 'marketing'])
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.complete_data_only = config.get('complete_data_only', True)
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from Substack using web scraping.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        for keyword in self.keywords:
            try:
                # Search Substack for the keyword using the website search
                search_url = f"https://substack.com/search?q={keyword}&type=publication"
                logging.info(f"Searching Substack for keyword: {keyword}")
                
                response = requests.get(
                    search_url, 
                    headers={'User-Agent': self.user_agent}, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find publication cards on the search page
                    publication_cards = soup.select('div.publication-card, div.substackCard')
                    
                    logging.info(f"Found {len(publication_cards)} publications for '{keyword}'")
                    
                    for card in publication_cards:
                        # Extract publication details
                        newsletter = self._extract_publication_from_card(card)
                        
                        # If we need complete data and this entry is not complete, skip it
                        if self.complete_data_only and not self._is_complete(newsletter):
                            continue
                        
                        newsletters.append(newsletter)
                else:
                    logging.error(f"Failed to search Substack website, status code: {response.status_code}")
            except Exception as e:
                logging.error(f"Error searching Substack for {keyword}: {str(e)}")
        
        return newsletters
    
    def _extract_publication_from_card(self, card) -> Dict:
        """Extract publication details from a search result card.
        
        Args:
            card: BeautifulSoup element representing a publication card
        
        Returns:
            Newsletter data dictionary
        """
        # Extract name
        name_elem = card.select_one('h3, .publicationTitle')
        name = name_elem.text.strip() if name_elem else ""
        
        # Extract link
        link_elem = card.select_one('a.publication-title, a.substackUrl')
        link = link_elem['href'] if link_elem and 'href' in link_elem.attrs else ""
        if link and not link.startswith('http'):
            link = 'https://substack.com' + link
        
        # Extract publisher
        publisher_elem = card.select_one('div.publisher-name, .authorName')
        publisher = publisher_elem.text.strip() if publisher_elem else ""
        
        # Create base newsletter data
        newsletter = {
            'name': name,
            'link': link,
            'publisher': publisher,
            'email': '',
            'subscribers': None,
            'social_media': {},
            'source': 'substack'
        }
        
        # Try to get additional details from publication page
        if newsletter['link']:
            try:
                # Fetch the publication homepage
                response = requests.get(
                    newsletter['link'],
                    headers={'User-Agent': self.user_agent},
                    timeout=15
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Extract email
                    email = self._extract_email_from_page(soup, response.text)
                    if email:
                        newsletter['email'] = email
                    
                    # Extract social media
                    social_media = self._extract_social_media(soup)
                    if social_media:
                        newsletter['social_media'] = social_media
                    
                    # Extract subscriber count
                    subscribers = self._extract_subscriber_count_from_page(soup, response.text)
                    if subscribers:
                        newsletter['subscribers'] = subscribers
            except Exception as e:
                logging.error(f"Error getting additional details for {name}: {str(e)}")
        
        return newsletter
    
    def _extract_subscriber_count_from_page(self, soup: BeautifulSoup, text: str) -> Optional[int]:
        """Extract subscriber count from publication homepage.
        
        Args:
            soup: BeautifulSoup object of the publication homepage
            text: Raw text of the publication homepage
        
        Returns:
            Subscriber count or None if not available
        """
        # Try to find subscriber count in the page text
        subscriber_patterns = [
            r'(\d[\d,\.]+)\s*(?:subscriber|reader)',
            r'(\d[\d,\.]+)\s*(?:people subscribe|members)',
            r'(?:grow|built|with|over)\s+(\d[\d,\.]+)\s*(?:subscriber)'
        ]
        
        for pattern in subscriber_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Get the largest number match
                max_subscribers = 0
                for match in matches:
                    try:
                        number_str = match.replace(',', '').replace('.', '')
                        subscribers = int(number_str)
                        max_subscribers = max(max_subscribers, subscribers)
                    except (ValueError, AttributeError):
                        pass
                
                if max_subscribers > 0:
                    return max_subscribers
        
        # Look for elements that might contain subscriber count
        for element in soup.select('div.stats-item, div.subscriber-count, span.subscriber-count, .subscriberCount'):
            text = element.text.strip()
            # Look for numbers in the text
            match = re.search(r'(\d[\d,\.]+)', text)
            if match:
                try:
                    number_str = match.group(1).replace(',', '').replace('.', '')
                    return int(number_str)
                except ValueError:
                    pass
        
        return None
    
    def _extract_email_from_page(self, soup: BeautifulSoup, text: str) -> str:
        """Extract contact email from publication homepage.
        
        Args:
            soup: BeautifulSoup object of the publication homepage
            text: Raw text of the publication homepage
        
        Returns:
            Contact email or empty string if not available
        """
        # Look for mailto links
        for link in soup.select('a[href^="mailto:"]'):
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href[7:]  # Remove 'mailto:' prefix
                # Verify it's a valid email format
                if re.match(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', email):
                    return email
        
        # Look for email pattern in the entire page text
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        if matches:
            # Filter out common false positives
            filtered_emails = [
                email for email in matches 
                if not any(ignore in email.lower() for ignore in ['example.com', 'test@', 'user@'])
            ]
            if filtered_emails:
                return filtered_emails[0]  # Return the first valid email
        
        return ''
    
    def _extract_social_media(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract social media links from publication homepage.
        
        Args:
            soup: BeautifulSoup object of the publication homepage
        
        Returns:
            Dictionary of social media platform names and links
        """
        social_media = {}
        
        # Common social media domains
        platforms = {
            'twitter.com': 'twitter',
            'x.com': 'twitter',
            'facebook.com': 'facebook',
            'linkedin.com': 'linkedin',
            'instagram.com': 'instagram',
            'youtube.com': 'youtube'
        }
        
        # Look for links to social media platforms
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            for domain, platform in platforms.items():
                if domain in href:
                    social_media[platform] = href
        
        return social_media
    
    def _is_complete(self, newsletter: Dict) -> bool:
        """Check if a newsletter entry has complete data.
        
        Args:
            newsletter: Newsletter data dictionary
        
        Returns:
            True if the newsletter has complete data, False otherwise
        """
        required_fields = ['name', 'link', 'publisher', 'email', 'subscribers']
        
        for field in required_fields:
            if not newsletter.get(field):
                return False
        
        return True