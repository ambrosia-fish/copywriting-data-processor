import logging
import os
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Optional, Tuple

import feedparser
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.collectors.base_collector import BaseCollector


class RssCollector(BaseCollector):
    """Collects newsletter data from RSS feeds."""
    
    def __init__(self, config: Dict):
        """Initialize the RSS collector.
        
        Args:
            config: Configuration dictionary for the RSS collector
        """
        self.config = config
        self.websites = config.get('websites', [])
        self.max_feeds_per_site = config.get('max_feeds_per_site', 3)
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    
    def collect(self) -> List[Dict]:
        """Collect newsletter data from RSS feeds.
        
        Returns:
            List of newsletter data dictionaries
        """
        newsletters = []
        
        # Find RSS feeds for each website
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_site = {
                executor.submit(self._find_rss_feeds, site): site 
                for site in self.websites
            }
            
            for future in tqdm(future_to_site, desc="Finding RSS feeds"):
                site = future_to_site[future]
                try:
                    feeds = future.result()
                    logging.info(f"Found {len(feeds)} feeds for {site}")
                    
                    # Limit the number of feeds per site
                    feeds = feeds[:self.max_feeds_per_site]
                    
                    for feed_url in feeds:
                        try:
                            newsletter = self._parse_rss_feed(feed_url)
                            if newsletter:
                                newsletters.append(newsletter)
                        except Exception as e:
                            logging.error(f"Error parsing feed {feed_url}: {str(e)}")
                except Exception as e:
                    logging.error(f"Error finding RSS for {site}: {str(e)}")
        
        return newsletters
    
    def _find_rss_feeds(self, website: str) -> List[str]:
        """Find RSS feeds for a website.
        
        Args:
            website: Website domain to check
        
        Returns:
            List of RSS feed URLs
        """
        if not website.startswith('http'):
            website = f'https://{website}'
        
        feeds = []
        try:
            # Check common RSS feed locations
            common_paths = [
                '/feed/',
                '/rss/',
                '/feed/rss/',
                '/feed.xml',
                '/rss.xml',
                '/atom.xml',
                '/rss/feed/',
                '/blog/feed/',
                '/blog/rss/',
                '/index.xml'
            ]
            
            # Try to get the homepage
            response = requests.get(
                website, 
                headers={'User-Agent': self.user_agent}, 
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for RSS feed links in the HTML
                for link in soup.find_all('link', type=re.compile(r'(rss|atom|xml)')):
                    if 'href' in link.attrs:
                        href = link['href']
                        if href.startswith('/'):
                            href = website + href
                        elif not href.startswith('http'):
                            href = website + '/' + href
                        feeds.append(href)
                
                # Check common paths if no feeds found
                if not feeds:
                    for path in common_paths:
                        feed_url = website + path
                        try:
                            feed_response = requests.get(
                                feed_url, 
                                headers={'User-Agent': self.user_agent}, 
                                timeout=5
                            )
                            if feed_response.status_code == 200 and \
                               ('xml' in feed_response.headers.get('Content-Type', '')):
                                feeds.append(feed_url)
                        except:
                            continue
        except Exception as e:
            logging.error(f"Error checking website {website}: {str(e)}")
        
        return feeds
    
    def _parse_rss_feed(self, feed_url: str) -> Optional[Dict]:
        """Parse an RSS feed to extract newsletter information.
        
        Args:
            feed_url: URL of the RSS feed
        
        Returns:
            Newsletter data dictionary or None if parsing failed
        """
        feed = feedparser.parse(feed_url)
        
        if not feed.entries:
            return None
        
        # Extract publisher name
        publisher = feed.feed.get('publisher', '')
        if not publisher and 'author' in feed.feed:
            publisher = feed.feed.get('author', '')
        if not publisher and 'authors' in feed.feed and feed.feed.authors:
            publisher = feed.feed.authors[0].get('name', '')
        
        # Extract contact email
        email = ''
        if 'author_detail' in feed.feed and 'email' in feed.feed.author_detail:
            email = feed.feed.author_detail.email
        
        # Extract links to find possible social media
        social_media = {}
        if 'links' in feed.feed:
            for link in feed.feed.links:
                url = link.get('href', '')
                if any(sm in url for sm in ['twitter.com', 'linkedin.com', 'facebook.com', 'instagram.com']):
                    platform = next((sm for sm in ['twitter', 'linkedin', 'facebook', 'instagram'] if sm in url), '')
                    if platform:
                        social_media[platform] = url
        
        # Try to estimate subscriber count (this is speculative at best)
        # We'll leave this for the subscriber formatter to handle
        subscribers = None
        
        return {
            'name': feed.feed.get('title', os.path.basename(feed_url)),
            'link': feed.feed.get('link', feed_url),
            'publisher': publisher,
            'email': email,
            'subscribers': subscribers,
            'social_media': social_media,
            'source': 'rss'
        }