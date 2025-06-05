# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright browser (required for web scraping)
playwright install firefox

# Run the crawler
python src/main.py -k "关键词" -p 1

# Setup configuration (first time use)
cp src/config.example.py config.py
# Then edit config.py with valid XHS_COOKIE
```

## Project Architecture

This is a Xiaohongshu (Little Red Book) web scraper built with Python using Playwright for browser automation.

### Core Components

- **XHSCrawler class** (`src/crawler.py`): Main crawler implementation using Playwright with Firefox
- **Main entry point** (`src/main.py`): CLI interface for running searches
- **Configuration** (`config.py`): Contains cookies and crawler settings (copy from `config.example.py`)

### Key Architecture Details

- Uses Playwright's Firefox browser in headless mode for web scraping
- Implements cookie-based authentication for Xiaohongshu access
- Two-stage process: search for notes, then extract detailed content
- Built-in random delays and error handling for robust scraping
- Data export to CSV format with pandas

### Data Flow

1. Search notes by keyword using encoded URL parameters
2. Extract note IDs and URLs from search results using multiple CSS selectors as fallbacks
3. Visit individual note pages to extract detailed content (title, content)
4. Save aggregated data to CSV in `output/data/` directory

### Configuration Requirements

- **XHS_COOKIE**: Valid Xiaohongshu session cookie (required for authentication)
- **OUTPUT_DIR**: Directory for logs and data output (default: "output")
- Browser automation requires Firefox installation via Playwright

### Important Implementation Notes

- Uses multiple CSS selector strategies as fallbacks for different page layouts
- Implements proper error handling for network timeouts and missing elements
- Logs extensively using loguru for debugging and monitoring
- Random delays between requests to avoid rate limiting