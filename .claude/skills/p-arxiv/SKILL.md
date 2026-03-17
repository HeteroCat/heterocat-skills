---
name: arxiv
description: Search and retrieve academic papers from arXiv using the arXiv API. Use when users want to find research papers, search by author/title/abstract, get paper metadata, download paper information, or explore academic literature in physics, mathematics, computer science, and related fields.
---

# arXiv API Skill

Search and retrieve academic papers from arXiv's open-access repository.

## Quick Start

### Basic Search

Search for papers by keywords:

```python
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

def search_arxiv(query, max_results=10):
    """Search arXiv for papers matching the query."""
    base_url = "http://export.arxiv.org/api/query"
    params = f"?search_query=all:{urllib.parse.quote(query)}&max_results={max_results}"

    with urllib.request.urlopen(base_url + params) as response:
        return response.read().decode('utf-8')

# Example usage
xml_result = search_arxiv("quantum computing", max_results=5)
```

### Search by Author

```python
def search_by_author(author_name, max_results=10):
    """Search for papers by a specific author."""
    base_url = "http://export.arxiv.org/api/query"
    params = f"?search_query=au:{urllib.parse.quote(author_name)}&max_results={max_results}"

    with urllib.request.urlopen(base_url + params) as response:
        return response.read().decode('utf-8')
```

### Get Paper by ID

```python
def get_paper_by_id(arxiv_id):
    """Retrieve a specific paper by its arXiv ID."""
    base_url = "http://export.arxiv.org/api/query"
    params = f"?id_list={arxiv_id}"

    with urllib.request.urlopen(base_url + params) as response:
        return response.read().decode('utf-8')
```

## Search Query Syntax

### Field Prefixes

| Prefix | Field |
|--------|-------|
| `ti:` | Title |
| `au:` | Author |
| `abs:` | Abstract |
| `co:` | Comment |
| `jr:` | Journal Reference |
| `cat:` | Subject Category |
| `rn:` | Report Number |
| `all:` | All fields |

### Boolean Operators

- `AND` - Both conditions must match
- `OR` - Either condition matches
- `ANDNOT` - Exclude matching results

```python
# Complex query example
query = "au:del_maestro AND ti:checkerboard"
query = "cat:cs.AI AND abs:machine learning"
query = "all:neural network ANDNOT ti:review"
```

### Date Filtering

```python
# Papers submitted in 2023
date_query = "submittedDate:[202301010000 TO 202312312359]"

# Combine with other queries
full_query = f"au:smith AND {date_query}"
```

## Parsing Results

The API returns Atom 1.0 XML. Parse it to extract paper information:

```python
import xml.etree.ElementTree as ET

def parse_arxiv_response(xml_data):
    """Parse arXiv API XML response into a list of paper dictionaries."""
    ns = {
        'atom': 'http://www.w3.org/2005/Atom',
        'arxiv': 'http://arxiv.org/schemas/atom'
    }

    root = ET.fromstring(xml_data)
    papers = []

    for entry in root.findall('atom:entry', ns):
        paper = {
            'title': entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else '',
            'summary': entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else '',
            'id': entry.find('atom:id', ns).text if entry.find('atom:id', ns) is not None else '',
            'published': entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else '',
            'updated': entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else '',
            'authors': [author.find('atom:name', ns).text for author in entry.findall('atom:author', ns)],
            'categories': [cat.get('term') for cat in entry.findall('atom:category', ns)],
            'primary_category': entry.find('arxiv:primary_category', ns).get('term') if entry.find('arxiv:primary_category', ns) is not None else '',
            'comment': entry.find('arxiv:comment', ns).text if entry.find('arxiv:comment', ns) is not None else '',
            'journal_ref': entry.find('arxiv:journal_ref', ns).text if entry.find('arxiv:journal_ref', ns) is not None else '',
            'doi': entry.find('arxiv:doi', ns).text if entry.find('arxiv:doi', ns) is not None else '',
            'pdf_url': None
        }

        # Find PDF link
        for link in entry.findall('atom:link', ns):
            if link.get('title') == 'pdf':
                paper['pdf_url'] = link.get('href')
                break

        papers.append(paper)

    return papers
```

## API Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `search_query` | Search terms with field prefixes | - |
| `id_list` | Comma-separated arXiv IDs | - |
| `start` | Starting index (0-based) | 0 |
| `max_results` | Number of results to return | 10 |
| `sortBy` | Sort order: `relevance`, `lastUpdatedDate`, `submittedDate` | relevance |
| `sortOrder` | `ascending` or `descending` | descending |

## Usage Limits

- Maximum results per query: 30,000 total
- Maximum per request (`max_results`): 2,000
- Recommended delay between calls: 3 seconds
- Results update daily at midnight

## Best Practices

1. **Cache results** - Store responses to avoid repeated API calls
2. **Respect rate limits** - Add delays between requests
3. **URL encode queries** - Use `urllib.parse.quote()` for special characters
4. **Handle pagination** - Use `start` parameter for large result sets

## Attribution

When using arXiv data, include this attribution:
> "Data provided by arXiv.org"

See [references/api_reference.md](references/api_reference.md) for complete API documentation.
