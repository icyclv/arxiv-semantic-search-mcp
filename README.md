# arXiv Search MCP

A lightweight [Model Context Protocol](https://modelcontextprotocol.io/) server that lets AI assistants query the arXiv API. It provides two powerful search approaches:

- **Semantic Search**: Uses vector embeddings to understand the meaning of your query, powered by [ArxivSearch](https://hub.arxiv-search.cn)
  > **Note**: Currently, semantic search only supports papers in Computer Science (cs.*) categories
- **Keyword Search**: Supports structured queries with multiple filters including categories, date ranges, and field-specific searches
  > Note: Supports papers from all arXiv categories

## Requirements

* Python 3.12 or higher
* [uv](https://docs.astral.sh/uv/) package manager (dependency resolver & runner)

## Getting Started

### 1. Clone & install dependencies

```bash
# Clone the repository
git clone https://github.com/icyclv/arxiv-semantic-search-mcp.git
cd arxiv-semantic-search-mcp

# Install all project dependencies listed in pyproject.toml
uv sync
```

### 2. Run the server locally

```bash
# Start the MCP server
uv run main.py
```

## Editor / Client Configuration

To use this MCP server with your AI assistant tools (e.g. Claude Desktop, VS Code MCP extension), add the following configuration:

```json
{
  "mcpServers": {
    "arxiv-semantic-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/arxiv-semantic-search-mcp",  // Replace with actual path
        "run",
        "main.py"
      ]
    }
  }
}
```

Note: Replace `/path/to/arxiv-semantic-search-mcp` with the actual path where you cloned the repository.

## Available Functions

| Function          | Description                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `search_semantic` | Semantic search for papers using natural language queries and embeddings |
| `search_keyword`  | Search papers using structured keyword queries with multiple filters    |
| `get_details`     | Retrieve detailed information for a specific paper by arXiv ID         |
| `get_categories`  | Get list of arXiv categories and their descriptions                    |
| `get_current_time`| Get current server time in specified format                            |

See `src/server.py` for detailed documentation and examples.

## Usage Examples

### Semantic Search
```python
# Search for papers about deep learning in computer vision
search_semantic(
    query="recent advances in vision transformers for medical image segmentation",
    categories=["cs.CV", "cs.AI"]
)
```

### Keyword Search
```python
# Search for recent machine learning papers in multiple categories
search_keyword(
    categories=["cs.AI", "cs.LG"],
    start_date="2024-01-01",
    all_fields="transformer",
    sort_by="submittedDate",
    sort_order="descending"
)
```

### Get Paper Details
```python
# Get detailed information for a specific paper
get_details("2401.00001")
```

## License

This project is released under the MIT License.