# UniGraph Parser

A powerful tool for extracting structured information from codebases using AST parsing and LLM analysis. UniGraph Parser analyzes repositories to identify code structure, dependencies, and relationships between different components.

## Features

- 🔍 **Multi-language support** - Support for all programming languages
- 🏗️ **AST-based parsing** - Uses Tree-sitter for accurate syntax analysis
- 🤖 **LLM-powered analysis** - Leverages large language models for semantic understanding
- 📈 **Incremental processing** - Process specific files or entire repositories
- 🔎 **Analysis tools** - File summaries and definition analysis capabilities

## Installation

### From Source

```bash
git clone https://github.com/FSoft-AI4Code/UniGraph.git
cd UniGraph
pip install -e .
```

or 
```bash
pip install git+https://github.com/FSoft-AI4Code/UniGraph.git
```

## Quick Start

### 1. Set up LLM service

UniGraph Parser requires an LLM service:

```bash
export LLM_MODEL="<llm_model>"
export LLM_BASE_URL="<llm_base_url>"
export LLM_API_KEY="<llm_api_key>"
```

Or create a `.env` file:

```.env
LLM_MODEL=llm_model
LLM_BASE_URL=llm_base_url
LLM_API_KEY=llm_api_key
```

### 2. Parse a repository

```bash
# Parse entire repository
unigraph parse --repo-path /path/to/your/repository --output-dir ./output

# Parse specific files
unigraph parse --repo-path /path/to/repository --output-dir ./output --file-paths "file1.py,file2.js"
```

## CLI Commands

### Repository Parsing

Parse the entire repository or specific files:

```bash
unigraph parse --repo-path /path/to/repo --output-dir ./output
```

**Options:**
- `--repo-path` (required): Path to the repository
- `--output-dir` (required): Output directory for results
- `--file-paths` (optional): Comma-separated list of specific files to parse
- `--max-concurrent` (default: 5): Maximum concurrent file processing
- `--log-level` (default: INFO): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

### File Summary Analysis

Generate a concise summary of a file showing node structure:

```bash
unigraph file-summary \
  --repo-path /path/to/repo \
  --output-dir ./output \
  --file-path "src/main.py"
```

### Definition Analysis

Get detailed analysis for a specific code element:

```bash
unigraph get-definition \
  --repo-path /path/to/repo \
  --output-dir ./output \
  --file-path "/absolute/path/to/src/main.py" \
  --node-name "SearchProvider"
```

### CLI Help

```bash
# Get general help
unigraph --help

# Get help for specific commands
unigraph parse --help
unigraph file-summary --help
unigraph get-definition --help
```

## Python SDK Usage

### Basic Repository Parsing

```python
import asyncio
from unigraph.parsing.repository import parse_repository_incrementally

async def main():
    # Parse repository
    output_file = await parse_repository_incrementally(
        repo_path="/path/to/repository",
        output_dir="./output",
        max_concurrent=5
    )
    print(f"Results saved to: {output_file}")

asyncio.run(main())
```

### File Summary Analysis

```python
from unigraph.analyzing import FileSummaryAnalyzer

# Create analyzer from results
analyzer = FileSummaryAnalyzer.from_aggregated_results("output/results.json")

# Analyze a specific file
summary = analyzer.analyze_file_summary("src/main.py")
formatted_summary = analyzer.format_file_summary(summary)
print(formatted_summary)
```

### Definition Analysis

```python
from unigraph.analyzing import DefinitionAnalyzer

# Create analyzer from results
analyzer = DefinitionAnalyzer.from_aggregated_results("output/results.json", on_demand=True)

# Analyze a specific node
analysis = analyzer.get_definition_analysis(
    absolute_file_path="/absolute/path/to/src/main.py",
    node_name="SearchProvider"
)

formatted_analysis = analyzer.format_definition_analysis(analysis)
print(formatted_analysis)
```

## Output Format

The parser generates a JSON file with structured information about your codebase:

```json
{
  "repository": {
    "name": "my-project",
    "path": "/path/to/repo",
    "total_files_processed": 42,
    "total_files_failed": 0,
    "failed_files": []
  },
  "nodes": [
    {
      "id": "src.main.WhisperModel",
      "implementation_file": "src/main.cpp",
      "start_line": 15,
      "end_line": 145,
      "type": "class"
    }
  ],
  "edges": [
    {
      "subject_id": "src.main.WhisperModel",
      "subject_implementation_file": "src/main.cpp",
      "object_id": "src.utils.Logger",
      "object_implementation_file": "src/utils.cpp",
      "type": "dependency"
    }
  ],
  "statistics": {
    "total_nodes": 156,
    "total_edges": 298,
    "nodes_by_type": {
      "class": 23,
      "function": 87,
      "variable": 46
    }
  }
}
```

