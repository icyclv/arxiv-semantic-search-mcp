"""MCP server implementation with tools and resources."""

import logging
from typing import Optional, List, Dict
import datetime  # 添加datetime导入

from fastmcp import FastMCP

from .arxiv_client import ArxivClient, ARXIV_MAJOR_CATEGORIES
from .semantic_search_client import SemanticSearchClient
from .models import SearchResult, ArxivPaper

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# Global clients
arxiv_client: Optional[ArxivClient] = None
semantic_search_client: Optional[SemanticSearchClient] = None

# Create MCP instance
mcp = FastMCP("arxiv-search-mcp")


async def startup():
    """Initialize the clients on server startup."""
    global arxiv_client, semantic_search_client
    logger.info("Initializing clients...")
    arxiv_client = ArxivClient()
    semantic_search_client = SemanticSearchClient()
    
    # Ensure clients are initialized before using them
    if arxiv_client is None or semantic_search_client is None:
        logger.error("Failed to initialize clients")
        raise RuntimeError("Failed to initialize clients")
    else:
        logger.info("Clients initialized successfully")


async def shutdown():
    """Close the clients on server shutdown."""
    global arxiv_client, semantic_search_client
    logger.info("Shutting down clients...")
    if arxiv_client:
        await arxiv_client.close()
        arxiv_client = None
    if semantic_search_client:
        await semantic_search_client.close()
        semantic_search_client = None
    logger.info("Clients shutdown complete")


@mcp.tool
async def search_semantic(
    query: str,
    page: int = 1,
    page_size: int = 10,
    use_rewrite: bool = False,
    categories: Optional[List[str]] = None,
    start_time: Optional[str] = None,  # YYYY-MM-DD
    end_time: Optional[str] = None,    # YYYY-MM-DD
) -> List[ArxivPaper]:
    """
    Searches for papers in the project's database using semantic vector similarity.
    
    Use this tool to find scientifically relevant papers based on natural language queries.
    This performs a semantic search using vector embeddings for better understanding of concepts,
    rather than just matching keywords.
    
    Parameters:
        query (str): Natural language query describing the research topic or concept of interest
        page (int): Page number for pagination (default: 1, must be >= 1)
        page_size (int): Number of results per page (default: 10, range: 1-15)
        use_rewrite (bool): Whether to use query rewriting to improve search quality (default: False)
        categories (List[str], optional): List of arXiv category codes to filter results
                                         (e.g., ["cs.AI", "cs.LG"])
        start_time (str, optional): Filter papers published on or after this date (format: YYYY-MM-DD)
        end_time (str, optional): Filter papers published on or before this date (format: YYYY-MM-DD)
    
    Returns:
        List[ArxivPaper]: List of papers ranked by semantic relevance to the query
    
    Examples:
        - Find papers on quantum computing applications:
          search_semantic("practical applications of quantum computing in cryptography")
        - Search for recent deep learning papers in computer vision:
          search_semantic("novel deep learning approaches for image segmentation", 
                          categories=["cs.CV"], 
                          start_time="2023-01-01")
        - Find papers about climate modeling with pagination:
          search_semantic("advanced climate modeling techniques considering ocean currents", 
                          page=2, 
                          page_size=15)
    """
    if semantic_search_client is None:
        logger.error("SemanticSearchClient not initialized. Call startup() first.")
        raise RuntimeError("SemanticSearchClient not initialized")
        
    logger.info(f"Semantic search: query='{query}', page={page}, page_size={page_size}")
    return await semantic_search_client.search(
        query, 
        page, 
        page_size, 
        use_rewrite, 
        categories, 
        start_time, 
        end_time
    )


@mcp.tool
async def get_details(arxiv_id: str) -> Optional[ArxivPaper]:
    """
    Retrieves detailed information for a single paper from the arXiv API.
    
    Use this tool to get comprehensive details about a specific paper when you have its arXiv ID.
    This provides more detailed information than what might be available in search results.
    
    Parameters:
        arxiv_id (str): The arXiv identifier for the paper (e.g., "2201.00001" or "2201.00001v1")
                        Can also accept the full arXiv URL format (e.g., "https://arxiv.org/abs/2201.00001")
    
    Returns:
        ArxivPaper: Object containing detailed paper information including title, authors,
                    abstract, publication date, categories, PDF link, and more.
                    Returns None if the paper cannot be found.
    
    Examples:
        - Get details for a specific paper:
          get_details("2201.00001")
        - Get details using a full URL:
          get_details("https://arxiv.org/abs/2201.00001")
        - Get details for a specific version:
          get_details("2201.00001v2")
    """
    if arxiv_client is None:
        logger.error("ArxivClient not initialized. Call startup() first.")
        raise RuntimeError("ArxivClient not initialized")
        
    logger.info(f"Fetching details for arXiv ID: {arxiv_id}")
    return await arxiv_client.get_details(arxiv_id)


@mcp.tool
def get_categories(major_category: Optional[str] = None) -> Dict[str, str]:
    """
    Retrieves the list of arXiv categories and their descriptions.
    
    Use this tool to get information about arXiv's taxonomy and classification system.
    You can either retrieve all categories or filter by a major category.
    
    Parameters:
        major_category (str, optional): Filter results by major category code 
                                       (e.g., "cs" for Computer Science, 
                                        "physics" for Physics, 
                                        "math" for Mathematics, etc.)
                                       If not provided, returns all categories.
    
    Returns:
        Dict[str, str]: Dictionary mapping category codes to their descriptions
                       (e.g., {"cs.AI": "Artificial Intelligence", 
                               "cs.CL": "Computation and Language"})
    
    Examples:
        - Get all arXiv categories:
          get_categories()
        - Get only Computer Science categories:
          get_categories("cs")
        - Get only Physics categories:
          get_categories("physics")
    """
    if arxiv_client is None:
        logger.error("ArxivClient not initialized. Call startup() first.")
        raise RuntimeError("ArxivClient not initialized")
        
    logger.info(f"Fetching categories for major category: {major_category}")
    return arxiv_client.get_categories(major_category)


@mcp.tool
def get_current_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Returns the current date and time.
    
    Use this tool to get the server's current time, which can be used for logging, timestamp generation, 
    or other scenarios requiring the current time.
    
    Args:
        format (str, optional): Date time format string following Python's datetime format specification.
                               Default format: year-month-day hour:minute:second (%Y-%m-%d %H:%M:%S)
    
    Returns:
        str: Formatted current date and time string
    
    Examples:
        - Get current time in default format:
          get_current_time()  # Returns something like "2023-10-15 14:30:25"
        - Get current time in custom format:
          get_current_time("%Y/%m/%d %H:%M:%S")  # Returns something like "2023/10/15 14:30:25"
        - Get only the date portion:
          get_current_time("%Y-%m-%d")  # Returns something like "2023-10-15"
    """
    logger.info(f"Getting current time with format: {format}")
    now = datetime.datetime.now()
    return now.strftime(format)

@mcp.tool
async def search_keyword(
    page: int = 1,
    page_size: int = 10,
    sort_by: str = "submittedDate",
    sort_order: str = "descending",
    title: Optional[str] = None,
    author: Optional[str] = None,
    abstract: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    all_fields: Optional[str] = None,
) -> List[ArxivPaper]:
    """
    Searches for papers on the public arXiv API using structured keyword queries.
    
    Use this tool to find scientific papers on arXiv by specifying various search criteria.
    At least one search criterion (title, author, abstract, category, or all_fields) must be provided.
    
    Note: Keyword queries often return empty results if the terms are too specific or uncommon.
    For more natural language queries and better concept understanding, consider using search_semantic
    instead, which uses vector embeddings for more flexible matching.
    
    Parameters:
        page (int): Page number for pagination (default: 1, must be >= 1)
        page_size (int): Number of results per page (default: 10, range: 1-15)
        sort_by (str): Field to sort results by (options: "submittedDate", "relevance", "lastUpdatedDate")
        sort_order (str): Order of sorting (options: "descending", "ascending")
        title (str, optional): Search for papers with this text in the title (use quotes for exact phrases)
        author (str, optional): Search for papers by this author name (surname or full name)
        abstract (str, optional): Search for papers with this text in the abstract
        category (str, optional): Filter by arXiv category code (e.g., "cs.AI", "physics.optics")
        start_date (str, optional): Filter papers submitted on or after this date (format: YYYY-MM-DD)
        end_date (str, optional): Filter papers submitted on or before this date (format: YYYY-MM-DD)
        all_fields (str, optional): Search across all fields (title, abstract, author, comments)
    
    Returns:
        List[ArxivPaper]: Object containing matching papers and total count of results
    
    Examples:
        - Search for recent machine learning papers:
          search_keyword(category="cs.LG", page_size=5)
        - Search for papers by a specific author on quantum computing:
          search_keyword(author="Feynman", abstract="quantum computing", page_size=10)
        - Search for papers from 2023 with pagination:
          search_keyword(all_fields="transformers", start_date="2023-01-01", end_date="2023-12-31", page=2)
    """
    if arxiv_client is None:
        logger.error("ArxivClient not initialized. Call startup() first.")
        raise RuntimeError("ArxivClient not initialized")
        
    query_parts = []
    if title:
        query_parts.append(f'ti:"{title}"')
    if author:
        query_parts.append(f'au:"{author}"')
    if abstract:
        query_parts.append(f'abs:"{abstract}"')
    if category:
        query_parts.append(f'cat:{category}')
    if all_fields:
        query_parts.append(f'all:{all_fields}')

    if start_date and end_date:
        try:
            start_date_formatted = start_date.replace("-", "") + "0000"
            end_date_formatted = end_date.replace("-", "") + "2359"
            query_parts.append(f"submittedDate:[{start_date_formatted} TO {end_date_formatted}]")
        except Exception as e:
            logger.error(f"Invalid date format provided: {e}")
            # It's better to raise an exception here, FastMCP will handle it
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.")

    if not query_parts:
        raise ValueError("At least one search criterion (title, author, etc.) must be provided.")

    query = " AND ".join(query_parts)

    # Convert page, page_size to start index and max_results for ArxivClient
    start = (page - 1) * page_size
    max_results = page_size

    logger.info(f"Constructed keyword search: query='{query}', page={page}, page_size={page_size}")
    return await arxiv_client.search(query, max_results, start, sort_by, sort_order)


import asyncio

async def main():
    """Main entry point for the server."""
    # Initialize clients first
    await startup()
    
    try:
        # This is a workaround for the fact that mcp.run() is a blocking call
        # and we need to run it in a separate thread to not block the event loop.
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: mcp.run(transport='stdio'))
    finally:
        # Clean up resources
        await shutdown()


if __name__ == "__main__":
    asyncio.run(main())