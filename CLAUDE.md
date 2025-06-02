# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Setup and Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the Crawler
```bash
# Basic usage (crawls every 10 seconds)
python mlit/crawler.py path/to/output.csv

# Custom interval
python mlit/crawler.py path/to/output.csv -i 30
```

### CSV Cleaning
```bash
python mlit/clean_csv.py original.csv cleaned.csv
```

### Testing and Code Quality
```bash
# Run tests
pytest

# Code formatting
black .

# Linting
flake8
```

### MCP Server
```bash
# Install MCP dependencies
pip install "mcp[cli]>=1.4.0"

# Run MCP server
python -m mlit.mcp_server

# Test MCP server (in development mode)
mcp dev mlit/mcp_server.py
```

## Architecture Overview

This is a system for accessing the Ministry of Land, Infrastructure, Transport and Tourism (MLIT) vehicle defect information database. The architecture consists of both traditional crawling tools and a modern MCP server interface:

### Core Components

1. **Crawler (`mlit/crawler.py`)**: Main crawling engine that scrapes vehicle defect data from the MLIT website
   - `Crawler` class handles pagination and data extraction from HTML tables
   - Uses BeautifulSoup for HTML parsing with 13-column table structure
   - Implements rate limiting with configurable intervals
   - Normalizes Japanese text using NFKC normalization

2. **Parser (`mlit/parser.py`)**: CSV processing utility for reading crawled data
   - Context manager for safe CSV file handling
   - Iterator interface for processing large datasets
   - UTF-8 encoding support for Japanese text

3. **CSV Cleaner (`mlit/clean_csv.py`)**: Post-processing utility to clean extracted data
   - Removes whitespace from all fields using `Normalizer.remove_spaces()`
   - Preserves original CSV structure and headers

4. **MCP Server (`mlit/mcp_server.py`)**: Model Context Protocol server for LLM integration
   - Provides tools for searching vehicle defects with parameters
   - Offers statistical analysis of defect data
   - Exports data in CSV format with cleaning options
   - Exposes resources for schema and sample data access

### Data Flow
**Traditional Flow:**
1. Crawler extracts data from MLIT website tables → Raw CSV
2. Clean CSV utility processes raw data → Cleaned CSV
3. Parser provides iteration interface for processed data

**MCP Server Flow:**
1. LLM sends request to MCP server tools
2. Server uses crawler to fetch real-time data from MLIT
3. Data is processed and returned in structured JSON or CSV format
4. LLM receives formatted data for analysis or presentation

### Key Technical Details
- Targets 13-column table structure from MLIT defect database
- Handles Japanese text normalization and whitespace removal
- Implements respectful crawling with configurable delays
- Uses context managers for proper resource handling
- MCP server provides async tools for real-time data access
- Supports filtering by manufacturer, model, date ranges