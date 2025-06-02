"""
MCP Server for MLIT Vehicle Defect Information Database

This MCP server provides tools and resources to access Japanese vehicle defect data
from the Ministry of Land, Infrastructure, Transport and Tourism (MLIT) database.
"""

import asyncio
import csv
import io
import json
import logging
import tempfile
from typing import List, Dict, Any, Optional
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import Resource, Tool

from mlit.crawler import Crawler, set_logger
from mlit.parser import Parser
from mlit.clean_csv import clean_csv


# Initialize MCP server
mcp = FastMCP("MLIT Vehicle Defects")

# Configure logging
set_logger(__name__)
logger = logging.getLogger(__name__)

# MLIT website configuration
MLIT_ROOT = "https://carinf.mlit.go.jp/jidosha/carinf/opn/"
MLIT_INIT_PAGE = "search.html?nccharset=59D56292&selCarTp=1&lstCarNo=000&txtFrDat=1000%2F01%2F01&txtToDat=9999%2F12%2F31&txtNamNm=&txtMdlNm=&txtEgmNm=&chkDevCd="


@mcp.tool()
async def search_vehicle_defects(
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    max_pages: int = 1,
    from_date: str = "1000/01/01",
    to_date: str = "9999/12/31"
) -> str:
    """
    Search for vehicle defect information from MLIT database.
    
    Args:
        manufacturer: Vehicle manufacturer name (Japanese)
        model: Vehicle model name (Japanese)
        max_pages: Maximum number of pages to crawl (default: 1)
        from_date: Start date in YYYY/MM/DD format (default: 1000/01/01)
        to_date: End date in YYYY/MM/DD format (default: 9999/12/31)
    
    Returns:
        JSON string containing vehicle defect records
    """
    try:
        # Build search URL with parameters
        search_params = f"search.html?nccharset=59D56292&selCarTp=1&lstCarNo=000&txtFrDat={from_date}&txtToDat={to_date}"
        
        if manufacturer:
            search_params += f"&txtNamNm={manufacturer}"
        if model:
            search_params += f"&txtMdlNm={model}"
            
        search_params += "&txtEgmNm=&chkDevCd="
        
        # Initialize crawler
        crawler = Crawler(MLIT_ROOT, search_params)
        
        # Get header information
        header = crawler.get_header()
        if len(header) != crawler.num_of_cols:
            raise ValueError(f"Unexpected table structure: {len(header)} columns instead of {crawler.num_of_cols}")
        
        # Collect records
        all_records = []
        pages_crawled = 0
        
        while crawler.page and pages_crawled < max_pages:
            records = crawler.get_records()
            all_records.extend(records)
            pages_crawled += 1
            
            if pages_crawled < max_pages:
                crawler.crawl_next()
                # Add small delay to be respectful
                await asyncio.sleep(1)
        
        # Format response
        result = {
            "header": header,
            "records": all_records,
            "total_records": len(all_records),
            "pages_crawled": pages_crawled,
            "search_parameters": {
                "manufacturer": manufacturer,
                "model": model,
                "from_date": from_date,
                "to_date": to_date
            }
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error searching vehicle defects: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def get_defect_statistics(
    manufacturer: Optional[str] = None,
    max_pages: int = 5
) -> str:
    """
    Get statistical summary of vehicle defects.
    
    Args:
        manufacturer: Filter by manufacturer name (Japanese)
        max_pages: Maximum pages to analyze (default: 5)
    
    Returns:
        JSON string with defect statistics
    """
    try:
        # Search for defects
        search_result = await search_vehicle_defects(
            manufacturer=manufacturer,
            max_pages=max_pages
        )
        
        data = json.loads(search_result)
        if "error" in data:
            return search_result
        
        records = data["records"]
        header = data["header"]
        
        # Calculate statistics
        stats = {
            "total_defects": len(records),
            "unique_manufacturers": set(),
            "unique_models": set(),
            "defect_types": {},
            "search_info": data["search_parameters"]
        }
        
        # Analyze records (assuming standard MLIT table structure)
        for record in records:
            if len(record) >= 3:  # Ensure we have manufacturer and model columns
                manufacturer_col = record[1] if len(record) > 1 else ""
                model_col = record[2] if len(record) > 2 else ""
                
                if manufacturer_col:
                    stats["unique_manufacturers"].add(manufacturer_col)
                if model_col:
                    stats["unique_models"].add(model_col)
        
        # Convert sets to lists for JSON serialization
        stats["unique_manufacturers"] = list(stats["unique_manufacturers"])
        stats["unique_models"] = list(stats["unique_models"])
        stats["manufacturer_count"] = len(stats["unique_manufacturers"])
        stats["model_count"] = len(stats["unique_models"])
        
        return json.dumps(stats, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error calculating statistics: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.tool()
async def export_defects_csv(
    manufacturer: Optional[str] = None,
    model: Optional[str] = None,
    max_pages: int = 3,
    clean_data: bool = True
) -> str:
    """
    Export vehicle defect data to CSV format.
    
    Args:
        manufacturer: Filter by manufacturer name (Japanese)
        model: Filter by model name (Japanese)
        max_pages: Maximum pages to export (default: 3)
        clean_data: Whether to clean whitespace from data (default: True)
    
    Returns:
        CSV data as string
    """
    try:
        # Search for defects
        search_result = await search_vehicle_defects(
            manufacturer=manufacturer,
            model=model,
            max_pages=max_pages
        )
        
        data = json.loads(search_result)
        if "error" in data:
            return search_result
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(data["header"])
        
        # Write records
        records = data["records"]
        if clean_data:
            # Apply cleaning to each field
            from .clean_csv import Normalizer
            cleaned_records = []
            for record in records:
                cleaned_record = [Normalizer.remove_spaces(field) for field in record]
                cleaned_records.append(cleaned_record)
            writer.writerows(cleaned_records)
        else:
            writer.writerows(records)
        
        csv_content = output.getvalue()
        output.close()
        
        return csv_content
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {e}")
        return f"Error: {str(e)}"


@mcp.resource("mlit://defects/schema")
async def get_defects_schema() -> str:
    """Get the schema/structure of MLIT defect data."""
    try:
        # Get a sample to determine schema
        crawler = Crawler(MLIT_ROOT, MLIT_INIT_PAGE)
        header = crawler.get_header()
        
        schema = {
            "table_name": "MLIT Vehicle Defects",
            "description": "Vehicle defect information from Japanese MLIT database",
            "columns": header,
            "column_count": len(header),
            "data_source": "https://carinf.mlit.go.jp/",
            "encoding": "UTF-8",
            "language": "Japanese"
        }
        
        return json.dumps(schema, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting schema: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@mcp.resource("mlit://defects/sample")
async def get_sample_data() -> str:
    """Get sample defect data for reference."""
    try:
        # Get just first page for sample
        result = await search_vehicle_defects(max_pages=1)
        data = json.loads(result)
        
        if "error" in data:
            return result
        
        # Return first 5 records as sample
        sample = {
            "header": data["header"],
            "sample_records": data["records"][:5],
            "note": "This is a sample of the first 5 records from the database"
        }
        
        return json.dumps(sample, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Error getting sample data: {e}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()