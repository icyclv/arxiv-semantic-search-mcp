"""Client for the project's internal semantic search apiservice."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

import httpx

from .models import ArxivPaper

logger = logging.getLogger(__name__)


class SemanticSearchClient:
    """Client for the project's internal semantic search apiservice.""" 

    def __init__(self, timeout: int = 30):
        # The URL for the semantic search service is hardcoded as per user request.
        self.base_url = "https://hub.arxivsearch.cn/api/search"
        self._client = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def search(
        self,
        query: str,
        page: int = 1,
        page_size: int = 10,
        use_rewrite: bool = False,
        categories: Optional[List[str]] = None,
        start_time: Optional[str] = None,  # YYYY-MM-DD
        end_time: Optional[str] = None,    # YYYY-MM-DD
    ) -> List[ArxivPaper]:
        """
        Performs a semantic search by calling the project's apiservice.

        Args:
            query: The natural language query.
            page: The page number for pagination.
            page_size: The number of results per page.
            use_rewrite: Whether to enable query rewriting on the backend.
            categories: A list of category codes to filter by.
            start_time: The start date for filtering (YYYY-MM-DD).
            end_time: The end date for filtering (YYYY-MM-DD).

        Returns:
            A list of ArxivPaper objects from the search results.
            
        Raises:
            ValueError: If invalid parameters are provided.
        """
        # Parameter validation
        if not query.strip():
            raise ValueError("Query content cannot be empty")
        
        if page < 1:
            raise ValueError("Page number must be greater than or equal to 1")
        
        if page_size < 1 or page_size > 15:
            raise ValueError("Number of results per page must be between 1 and 15")
            
        if start_time and end_time and start_time > end_time:
            raise ValueError("Start date cannot be later than end date")

        # This payload must match the SearchRequest struct defined in the service's IDL.
        payload = {
            "query": query,
            "page": page,
            "page_size": page_size,
            "search_by_paper": False,  # Indicates semantic search
            "use_rewrite": use_rewrite,
            "categories": categories,
            "start_time": start_time,
            "end_time": end_time,
        }
        # Filter out None values for optional fields, as the Go handler might
        # expect them to be absent from the JSON payload.
        payload = {k: v for k, v in payload.items() if v is not None}

        try:
            response = await self._client.post(self.base_url, json=payload)
            response.raise_for_status()
            response_data = response.json()
            
            # Assuming the response contains a 'papers' key with a list of paper dicts
            paper_dicts = response_data.get('papers', [])
            
            # Convert published_date from timestamp to YYYY-MM-DD string format
            for paper in paper_dicts:
                if 'published_date' in paper and isinstance(paper['published_date'], (int, float)):
                    # Convert timestamp to YYYY-MM-DD formatted string
                    timestamp = paper['published_date']
                    paper['published_date'] = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
            
            # Parse each paper dict into an ArxivPaper model
            papers = [ArxivPaper(**p) for p in paper_dicts]
            return papers
            
        except httpx.HTTPError as e:
            logger.error(f"Error during semantic search request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error parsing semantic search response: {e}")
            raise