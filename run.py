#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime

from src.collectors.substack_api_collector import SubstackApiCollector
from src.processors.email_verifier import EmailVerifier
from src.processors.subscriber_formatter import SubscriberFormatter
from src.writers.csv_writer import CsvWriter


def parse_args():
    parser = argparse.ArgumentParser(description='Collect newsletter data from Substack')
    parser.add_argument('--output', type=str, default='newsletters.csv',
                        help='Output CSV file path')
    parser.add_argument('--limit', type=int, default=3000,
                        help='Maximum number of newsletters to collect')
    parser.add_argument('--keywords', type=str, default='copywriting,marketing,email marketing,content marketing',
                        help='Comma-separated list of keywords to search for')
    parser.add_argument('--complete-only', action='store_true',
                        help='Only collect newsletters with complete data')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()


def setup_logger(verbose=False):
    """Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
    """
    level = logging.DEBUG if verbose else logging.INFO
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Configure logging
    log_filename = f"logs/newsletter_collector_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main entry point for the script."""
    # Parse command line arguments
    args = parse_args()
    
    # Set up logging
    setup_logger(args.verbose)
    
    # Print start message
    logging.info("Starting Newsletter Data Collector")
    logging.info(f"Output file: {args.output}")
    logging.info(f"Maximum newsletters: {args.limit}")
    logging.info(f"Keywords: {args.keywords}")
    logging.info(f"Complete data only: {args.complete_only}")
    
    # Start timer
    start_time = time.time()
    
    # Initialize the collector
    keywords = args.keywords.split(',')
    collector_config = {
        'keywords': keywords,
        'complete_data_only': args.complete_only
    }
    collector = SubstackApiCollector(collector_config)
    
    # Collect data
    logging.info("Collecting newsletter data...")
    newsletters = collector.collect()
    
    # Apply limit
    if len(newsletters) > args.limit:
        logging.info(f"Limiting to {args.limit} newsletters (from {len(newsletters)})")
        newsletters = newsletters[:args.limit]
    
    # Process the data
    logging.info("Processing newsletter data...")
    
    # Format subscriber counts
    subscriber_formatter = SubscriberFormatter({
        'default_if_unknown': False,
        'rounding': {
            'less_than_1000': 100,
            'less_than_10000': 1000,
            'less_than_500000': 10000,
            'above_500000': 100000,
            'million_plus': '1 Million+'
        }
    })
    newsletters = subscriber_formatter.process(newsletters)
    
    # Verify email addresses
    email_verifier = EmailVerifier({
        'method': 'basic'
    })
    newsletters = email_verifier.process(newsletters)
    
    # Write the data to CSV
    logging.info(f"Writing {len(newsletters)} newsletters to {args.output}")
    writer = CsvWriter({
        'path': args.output
    })
    writer.write(newsletters)
    
    # Print summary
    elapsed_time = time.time() - start_time
    logging.info(f"Completed in {elapsed_time:.2f} seconds")
    logging.info(f"Collected {len(newsletters)} newsletters")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())