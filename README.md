# Copywriting Newsletter Data Processor

This tool is designed to collect data on copywriting newsletters using RSS feeds and web scraping techniques. It can gather information such as newsletter names, direct links, publisher information, contact emails, subscriber counts (when available), and social media accounts.

## Features

- RSS feed discovery and processing
- Web scraping of newsletter information
- Email validation and cleaning
- Subscriber count standardization
- Google Sheets integration for data storage
- Multi-source data collection and deduplication

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

## Configuration

1. Copy the `config_template.json` to `config.json` and fill in your settings
2. If using Google Sheets, set up the Google Sheets API credentials (see the [setup instructions](docs/google_sheets_setup.md))

## Usage

### Basic Usage

```bash
# Run the full pipeline
python run.py

# Run only specific components
python run.py --sources=rss,feedspot,curated_lists
python run.py --skip-email-verification
python run.py --limit=500
```

### Advanced Usage

For more detailed instructions on customizing data collection and processing, see the [advanced usage documentation](docs/advanced_usage.md).

## Data Sources

The tool collects data from multiple sources:

1. **RSS Feeds**: Discovers and processes RSS feeds from marketing and copywriting websites
2. **Curated Lists**: Uses pre-compiled lists of top copywriting newsletters
3. **Feedspot Directory**: Extracts newsletter information from Feedspot's directory
4. **Substack Discovery**: Finds copywriting newsletters on Substack

## Output Format

The collected data is formatted according to requirements and can be exported to:

- Google Sheets (directly via API)
- CSV files
- Excel files
- JSON format

## License

MIT