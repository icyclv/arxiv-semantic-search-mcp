"""Data models for arXiv papers and search results."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator


class AISummary(BaseModel):
    """Represents an AI-generated summary of a paper."""
    model_version: str
    generated_at: int
    summary: str
    key_contributions: List[str]
    methodology: str
    experiments: str
    related_research: List[str]
    limitations: List[str]
    tags: List[str]


class ArxivPaper(BaseModel):
    """Represents a complete arXiv paper with all metadata."""
    arxiv_id: str = Field(description="arXiv identifier (e.g., 2301.00001)")
    title: str
    authors: List[str]
    abstract: str
    categories: List[str]
    published_date: str
    comment: Optional[str] = None
    ai_summary: Optional[AISummary] = None
    score: Optional[float] = None
    pdf_url: Optional[str] = None

    # Automatically populate the PDF URL if it's not provided
    @validator('pdf_url', always=True)
    def _populate_pdf_url(cls, v, values):
        """Constructs the PDF URL using the arXiv ID when not explicitly provided."""
        if v:  # Already provided by caller
            return v
        arxiv_id = values.get('arxiv_id')
        if arxiv_id:
            return f"https://arxiv.org/pdf/{arxiv_id}"
        return None


class SearchResult(BaseModel):
    """Represents search results from arXiv."""
    papers: List[ArxivPaper]
    total_results: int
