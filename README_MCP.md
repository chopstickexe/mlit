# MLIT Vehicle Defects MCP Server

An MCP (Model Context Protocol) server that provides access to Japanese vehicle defect data from the Ministry of Land, Infrastructure, Transport and Tourism (MLIT) database.

## Features

### Tools
- **`search_vehicle_defects`**: Search for vehicle defect records with optional filtering
- **`get_defect_statistics`**: Get statistical analysis of defect data  
- **`export_defects_csv`**: Export defect data in CSV format

### Resources
- **`mlit://defects/schema`**: Get the data schema/structure
- **`mlit://defects/sample`**: Get sample defect data for reference

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the MCP server:
```bash
python -m mlit.mcp_server
```

## Development

Test the server in development mode:
```bash
mcp dev mlit/mcp_server.py
```

## Configuration

For Claude Desktop integration, add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mlit-defects": {
      "command": "python",
      "args": ["-m", "mlit.mcp_server"],
      "cwd": "/path/to/mlit"
    }
  }
}
```

## Usage Examples

### Search Vehicle Defects
```python
# Search all defects (limited pages for performance)
await search_vehicle_defects(max_pages=2)

# Search by manufacturer
await search_vehicle_defects(manufacturer="トヨタ", max_pages=3)

# Search by manufacturer and model
await search_vehicle_defects(
    manufacturer="ホンダ", 
    model="アコード", 
    max_pages=2
)

# Search with date range
await search_vehicle_defects(
    from_date="2020-01-01",
    to_date="2023-12-31",
    max_pages=5
)
```

### Get Statistics
```python
# Overall statistics
await get_defect_statistics(max_pages=10)

# Statistics for specific manufacturer
await get_defect_statistics(manufacturer="日産", max_pages=5)
```

### Export Data
```python
# Export to CSV with cleaning
await export_defects_csv(
    manufacturer="マツダ",
    max_pages=3,
    clean_data=True
)
```

## Data Structure

The MLIT database contains 13 columns of vehicle defect information including:
- Manufacturer details
- Model information  
- Defect descriptions
- Dates and affected vehicle counts
- Recall information

All data is returned in Japanese as it appears in the original MLIT database.

## Rate Limiting

The server implements respectful crawling with:
- 1-second delays between page requests
- Configurable maximum pages per request
- Async implementation for better performance

## Error Handling

All tools return JSON responses with error information when issues occur:
```json
{
  "error": "Description of the error"
}
```