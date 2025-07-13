# arXiv Semantic Search MCP

A powerful semantic search engine for arXiv papers, built on the [Model Context Protocol](https://modelcontextprotocol.io/). This server enables AI assistants to perform intelligent, meaning-based searches across millions of academic papers, going beyond simple keyword matching.

Key Features:
* Semantic search powered by [ArxivSearch](https://hub.arxiv-search.cn) - find papers based on meaning, not just keywords
* Full arXiv API integration for comprehensive paper metadata and PDF access
* MCP-compliant interface for seamless AI assistant integration
* Advanced query construction for precise filtering

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

| Function              | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `search_papers`       | Perform semantic and keyword-based searches across arXiv papers            |
| `get_paper_details`   | Fetch complete metadata for a given paper                                  |
| `build_advanced_query`| Construct complex multi-field search queries with semantic understanding   |
| `get_arxiv_categories`| List all available arXiv subject categories                                |

### Search Capabilities

The semantic search functionality allows you to:
* Find papers based on natural language descriptions
* Discover related papers through semantic similarity
* Combine semantic search with traditional filters (date, category, author)
* Get contextually relevant results even with imperfect keyword matches

See `src/` for implementation details.

## License

This project is released under the MIT License.
