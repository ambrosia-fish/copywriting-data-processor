import logging
import re
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class SubstackApiCollector(BaseCollector):
    """Collects newsletter data from Substack using the unofficial API."""
    
    def __init__(self, config: Dict):
        """Initialize the Substack API collector.
        
        Args:
            config: Configuration dictionary for the Substack API collector
        """
        self.keywords = config.get('keywords', ['copywriting', 'marketing'])
        self.search_url = "https://substack.com/api/v1/search/publications"
        self.publication_url = "https://substack.com/api/v1/publication/{}"
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        self.complete_data_only = config.get('complete_data_only', True)
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from Substack using the unofficial API.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        for keyword in self.keywords:
            try:
                # Search Substack for the keyword
                logging.info(f"Searching Substack for keyword: {keyword}")
                
                params = {
                    'query': keyword,
                    'limit': 50,
                    'offset': 0,
                    'sort': 'top'
                }
                
                headers = {
                    'User-Agent': self.user_agent,
                    'Accept': 'application/json'
                }
                
                response = requests.get(
                    self.search_url, 
                    params=params,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        publications = data.get('publications', [])
                        
                        logging.info(f"Found {len(publications)} publications for '{keyword}'")
                        
                        for pub in publications:
                            # Get additional publication details
                            newsletter = self._get_publication_details(pub)
                            
                            # If we need complete data and this entry is not complete, skip it
                            if self.complete_data_only and not self._is_complete(newsletter):
                                continue
                            
                            newsletters.append(newsletter)
                    except ValueError:
                        logging.error(f"Invalid JSON response from Substack API")
                else:
                    logging.error(f"Failed to search Substack API, status code: {response.status_code}")
            except Exception as e:
                logging.error(f"Error searching Substack for {keyword}: {str(e)}")
        
        return newsletters
    
    def _get_publication_details(self, publication_data: Dict) -> Dict:
        """Get additional details for a publication.
        
        Args:
            publication_data: Basic publication data from search results
        
        Returns:
            Complete newsletter data dictionary
        """
        pub_id = publication_data.get('id')
        subdomain = publication_data.get('subdomain', '')
        name = publication_data.get('name', '')
        
        # Create base newsletter data
        newsletter = {
            'name': name,
            'link': f"https://{subdomain}.substack.com" if subdomain else "",
            'publisher': publication_data.get('author_name', ''),
            'email': '',
            'subscribers': self._extract_subscriber_count(publication_data),
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
                    
                    # Try to extract contact email
                    email = self._extract_email_from_page(soup)
                    if email:
                        newsletter['email'] = email
                    
                    # Try to extract social media links
                    social_media = self._extract_social_media(soup)
                    if social_media:
                        newsletter['social_media'] = social_media
                    
                    # If no subscriber count yet, try to extract it from the page
                    if not newsletter['subscribers']:
                        subscribers = self._extract_subscriber_count_from_page(soup)
                        if subscribers:
                            newsletter['subscribers'] = subscribers
            except Exception as e:
                logging.error(f"Error getting additional details for {name}: {str(e)}")
        
        return newsletter
    
    def _extract_subscriber_count(self, publication_data: Dict) -> Optional[int]:
        """Extract subscriber count from publication data.
        
        Args:
            publication_data: Publication data from Substack API
        
        Returns:
            Subscriber count or None if not available
        """
        return publication_data.get('total_subscribers')
    
    def _extract_subscriber_count_from_page(self, soup: BeautifulSoup) -> Optional[int]:
        """Extract subscriber count from publication homepage.
        
        Args:
            soup: BeautifulSoup object of the publication homepage
        
        Returns:
            Subscriber count or None if not available
        """
        # Substack often shows subscriber count in a statistics section
        # Look for elements that might contain this information
        for element in soup.select('div.stats-item, div.subscriber-count, span.subscriber-count'):
            text = element.text.strip()
            # Look for text with numbers followed by "subscribers" or similar
            if re.search(r'(\d[\d,\.]+)\s*(?:subscriber|reader)', text, re.IGNORECASE):
                match = re.search(r'(\d[\d,\.]+)', text)
                if match:
                    # Convert the number string to an integer
                    number_str = match.group(1).replace(',', '').replace('.', '')
                    try:
                        return int(number_str)
                    except ValueError:
                        pass
        
        return None
    
    def _extract_email_from_page(self, soup: BeautifulSoup) -> str:
        """Extract contact email from publication homepage.
        
        Args:
            soup: BeautifulSoup object of the publication homepage
        
        Returns:
            Contact email or empty string if not available
        """
        # Look for mailto links
        for link in soup.select('a[href^="mailto:"]'):
            href = link.get('href', '')
            if href.startswith('mailto:'):
                email = href[7:]  # Remove 'mailto:' prefix
                return email
        
        # Look for contact information in about section
        about_section = soup.select_one('div.about, section.about, div.description, section.description')
        if about_section:
            # Look for email pattern in text
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            match = re.search(email_pattern, about_section.text)
            if match:
                return match.group(0)
        
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