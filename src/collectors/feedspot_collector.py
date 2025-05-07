import logging
from typing import Dict, List

import requests
from bs4 import BeautifulSoup

from src.collectors.base_collector import BaseCollector


class FeedspotCollector(BaseCollector):
    """Collects newsletter data from Feedspot's directory."""
    
    def __init__(self):
        """Initialize the Feedspot collector."""
        self.feedspot_url = 'https://blog.feedspot.com/copywriting_blogs/'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from Feedspot.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        try:
            response = requests.get(
                self.feedspot_url, 
                headers={'User-Agent': self.user_agent}, 
                timeout=15
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the blog list elements
                blog_items = soup.select('div.blog-list-container div.blog-list')
                
                for item in blog_items:
                    try:
                        # Extract name and link
                        name_elem = item.select_one('div.blog-name a')
                        if not name_elem:
                            continue
                        
                        name = name_elem.text.strip()
                        link = name_elem['href']
                        
                        # Extract publisher
                        publisher_elem = item.select_one('div.blog-desc i')
                        publisher = publisher_elem.text.strip() if publisher_elem else ''
                        
                        # Extract email and social media
                        email = ''
                        social_media = {}
                        
                        social_icons = item.select('div.blog-contact a')
                        for icon in social_icons:
                            href = icon.get('href', '')
                            if 'mailto:' in href:
                                email = href.replace('mailto:', '')
                            elif any(sm in href for sm in ['twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com']):
                                platform = next((sm for sm in ['twitter', 'linkedin', 'facebook', 'instagram'] if sm in href), '')
                                if platform:
                                    social_media[platform] = href
                        
                        # Add to newsletters
                        newsletters.append({
                            'name': name,
                            'link': link,
                            'publisher': publisher,
                            'email': email,
                            'subscribers': None,  # Feedspot doesn't provide subscriber counts
                            'social_media': social_media,
                            'source': 'feedspot'
                        })
                    except Exception as e:
                        logging.error(f"Error parsing Feedspot item: {str(e)}")
            else:
                logging.error(f"Failed to fetch Feedspot page, status code: {response.status_code}")
        except Exception as e:
            logging.error(f"Error collecting from Feedspot: {str(e)}")
        
        return newsletters