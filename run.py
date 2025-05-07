#!/usr/bin/env python

import argparse
import json
import logging
import os
import sys
from datetime import datetime

from src.pipeline import Pipeline
from src.utils.logger import setup_logger


def parse_args():
    parser = argparse.ArgumentParser(description='Collect and process copywriting newsletter data')
    parser.add_argument('--config', type=str, default='config.json',
                        help='Path to configuration file')
    parser.add_argument('--sources', type=str,
                        help='Comma-separated list of sources to use (overrides config)')
    parser.add_argument('--skip-email-verification', action='store_true',
                        help='Skip email verification step')
    parser.add_argument('--limit', type=int,
                        help='Maximum number of newsletters to collect (overrides config)')
    parser.add_argument('--output', type=str,
                        help='Output format(s), comma-separated (google_sheets,csv,excel,json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')
    return parser.parse_args()


def load_config(config_path):
    if not os.path.exists(config_path):
        if os.path.exists('config_template.json'):
            logging.error(f"Configuration file {config_path} not found. "
                         f"Please copy config_template.json to {config_path} and update it.")
        else:
            logging.error(f"Configuration file {config_path} not found and no template available.")
        sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)


def update_config_from_args(config, args):
    if args.sources:
        sources = args.sources.split(',')
        for source in config['sources']:
            config['sources'][source]['enabled'] = (source in sources)
    
    if args.skip_email_verification:
        config['processing']['email_verification']['enabled'] = False
    
    if args.limit:
        config['processing']['limit'] = args.limit
    
    if args.output:
        outputs = args.output.split(',')
        for output in config['output']:
            config['output'][output]['enabled'] = (output in outputs)
    
    return config


def main():
    args = parse_args()
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logger(log_level)
    
    logging.info("Starting Copywriting Newsletter Data Processor")
    
    # Load and update configuration
    config = load_config(args.config)
    config = update_config_from_args(config, args)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Initialize and run the pipeline
    start_time = datetime.now()
    pipeline = Pipeline(config)
    newsletters = pipeline.run()
    end_time = datetime.now()
    
    # Print summary
    duration = (end_time - start_time).total_seconds()
    logging.info(f"Pipeline completed in {duration:.2f} seconds")
    logging.info(f"Collected data on {len(newsletters)} newsletters")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())