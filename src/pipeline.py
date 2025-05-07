import logging
from typing import Dict, List

from src.collectors.base_collector import BaseCollector
from src.collectors.curated_lists_collector import CuratedListsCollector
from src.collectors.feedspot_collector import FeedspotCollector
from src.collectors.rss_collector import RssCollector
from src.collectors.substack_collector import SubstackCollector
from src.processors.deduplicator import Deduplicator
from src.processors.email_verifier import EmailVerifier
from src.processors.subscriber_formatter import SubscriberFormatter
from src.writers.base_writer import BaseWriter
from src.writers.csv_writer import CsvWriter
from src.writers.excel_writer import ExcelWriter
from src.writers.google_sheets_writer import GoogleSheetsWriter
from src.writers.json_writer import JsonWriter


class Pipeline:
    def __init__(self, config: Dict):
        self.config = config
        self.collectors = self._initialize_collectors()
        self.processors = self._initialize_processors()
        self.writers = self._initialize_writers()
    
    def _initialize_collectors(self) -> List[BaseCollector]:
        collectors = []
        
        # Add RSS collector if enabled
        if self.config['sources']['rss']['enabled']:
            collectors.append(RssCollector(self.config['sources']['rss']))
        
        # Add Feedspot collector if enabled
        if self.config['sources']['feedspot']['enabled']:
            collectors.append(FeedspotCollector())
        
        # Add curated lists collector if enabled
        if self.config['sources']['curated_lists']['enabled']:
            collectors.append(CuratedListsCollector(
                self.config['sources']['curated_lists']
            ))
        
        # Add Substack collector if enabled
        if self.config['sources']['substack']['enabled']:
            collectors.append(SubstackCollector(
                self.config['sources']['substack']
            ))
        
        return collectors
    
    def _initialize_processors(self) -> List:
        processors = []
        
        # Add subscriber formatter
        processors.append(SubscriberFormatter(
            self.config['processing']['subscriber_count']
        ))
        
        # Add email verifier if enabled
        if self.config['processing']['email_verification']['enabled']:
            processors.append(EmailVerifier(
                self.config['processing']['email_verification']
            ))
        
        # Add deduplicator (always needed)
        processors.append(Deduplicator())
        
        return processors
    
    def _initialize_writers(self) -> List[BaseWriter]:
        writers = []
        
        # Add Google Sheets writer if enabled
        if self.config['output']['google_sheets']['enabled']:
            writers.append(GoogleSheetsWriter(
                self.config['output']['google_sheets']
            ))
        
        # Add CSV writer if enabled
        if self.config['output']['csv']['enabled']:
            writers.append(CsvWriter(
                self.config['output']['csv']
            ))
        
        # Add Excel writer if enabled
        if self.config['output']['excel']['enabled']:
            writers.append(ExcelWriter(
                self.config['output']['excel']
            ))
        
        # Add JSON writer if enabled
        if self.config['output']['json']['enabled']:
            writers.append(JsonWriter(
                self.config['output']['json']
            ))
        
        return writers
    
    def run(self) -> List[Dict]:
        # Collect data from all sources
        newsletters = []
        for collector in self.collectors:
            logging.info(f"Collecting data using {collector.__class__.__name__}")
            collector_data = collector.collect()
            logging.info(f"Collected {len(collector_data)} newsletters")
            newsletters.extend(collector_data)
        
        # Apply limit if set
        limit = self.config['processing']['limit']
        if limit and len(newsletters) > limit:
            logging.info(f"Limiting to {limit} newsletters (from {len(newsletters)})")
            newsletters = newsletters[:limit]
        
        # Process the collected data
        for processor in self.processors:
            logging.info(f"Processing data using {processor.__class__.__name__}")
            newsletters = processor.process(newsletters)
        
        # Write the processed data
        for writer in self.writers:
            logging.info(f"Writing data using {writer.__class__.__name__}")
            writer.write(newsletters)
        
        return newsletters