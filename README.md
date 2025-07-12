# arXiv Search MCP

A lightweight [Model Context Protocol](https://modelcontextprotocol.io/) server that lets AI assistants query the arXiv API. It exposes a simple set of functions for searching papers, retrieving metadata and downloading PDFs – all accessible through the MCP function-calling interface.

Semantic search capability based on [ArxivSearch](https://hub.arxiv-search.cn).

## Requirements

* Python 3.12+
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

Below is an example configuration for an MCP client that launches the server via **uv** (e.g. Claude Desktop, VS Code MCP extension, etc.):

```json
{
  "mcpServers": {
    "arxiv-semantic-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/arxiv-semantic-search-mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

## Available Functions

| Function              | Description                                   |
| --------------------- | --------------------------------------------- |
| `search_papers`       | Search arXiv with flexible query syntax       |
| `get_paper_details`   | Fetch complete metadata for a given paper     |
| `build_advanced_query`| Construct complex multi-field search queries  |
| `get_arxiv_categories`| List all available arXiv subject categories   |

See `src/` for implementation details.


## License

This project is released under the MIT License.