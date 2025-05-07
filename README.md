# Copywriting Newsletter Data Collector

A tool that collects data on copywriting newsletters from Substack, focusing on finding complete entries with all required information.

## What It Does

This tool searches Substack for copywriting and marketing newsletters, extracting:
- Name of Publication/Newsletter
- Direct link to the newsletter
- Owner/publisher name
- Contact email address
- Subscriber count
- Social media accounts (when available)

The tool is designed to **only save entries that have complete information** - ensuring your dataset is high quality and ready to use.

## Installation

```bash
# Clone the repository
git clone https://github.com/ambrosia-fish/copywriting-data-processor.git
cd copywriting-data-processor

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

Basic usage:

```bash
# Run with default settings
python run.py

# Specify output file
python run.py --output newsletters.csv

# Specify maximum number of newsletters to collect
python run.py --limit 500

# Specify search keywords
python run.py --keywords "copywriting,email marketing,content marketing"

# Only collect newsletters with complete data (name, link, publisher, email, subscriber count)
python run.py --complete-only

# Enable verbose logging
python run.py --verbose
```

## How It Works

1. Searches Substack for newsletters matching your keywords
2. Extracts available data using Substack's unofficial API
3. Enhances data by parsing newsletter homepages for additional information
4. Applies filtering to ensure only complete entries are saved
5. Formats subscriber counts according to your requirements
6. Verifies email addresses to ensure they're valid
7. Exports the collected data to a CSV file

## Requirements

- Python 3.7+
- Dependencies listed in requirements.txt
- Internet connection to access Substack

## License

MIT
