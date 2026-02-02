# arXiv API Complete Reference

## Base URL

```
http://export.arxiv.org/api/query
```

Supports both GET and POST requests. No authentication required.

## Query Parameters

### Core Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `search_query` | string | No* | Search terms with field prefixes |
| `id_list` | string | No* | Comma-separated arXiv IDs |
| `start` | integer | No | Starting index (0-based) | 0 |
| `max_results` | integer | No | Results per request | 10 |
| `sortBy` | string | No | Sort field | relevance |
| `sortOrder` | string | No | Sort direction | descending |

*At least one of `search_query` or `id_list` must be provided.

### Sort Options

- `relevance` - Relevance to query
- `lastUpdatedDate` - Most recently updated
- `submittedDate` - Submission date

### Sort Order

- `ascending` - Oldest first
- `descending` - Newest first (default)

## Search Fields

| Prefix | Field | Example |
|--------|-------|---------|
| `ti:` | Title | `ti:quantum computing` |
| `au:` | Author | `au:smith` |
| `abs:` | Abstract | `abs:machine learning` |
| `co:` | Comment | `co:revised` |
| `jr:` | Journal Reference | `jr:nature` |
| `cat:` | Subject Category | `cat:cs.AI` |
| `rn:` | Report Number | `rn:MIT-CSAIL-TR` |
| `all:` | All fields | `all:neural network` |

## Boolean Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `AND` | Both conditions | `au:smith AND ti:neural` |
| `OR` | Either condition | `cat:cs.AI OR cat:cs.LG` |
| `ANDNOT` | Exclude | `all:quantum ANDNOT ti:review` |

### Grouping

Use URL-encoded parentheses for complex queries:
- `%28` = `(`
- `%29` = `)`

```
%28au:smith OR au:jones%29 AND ti:machine learning
```

## Date Range Queries

Format: `[YYYYMMDDTTTT TO YYYYMMDDTTTT]` (24-hour GMT)

```
submittedDate:[202301010000 TO 202312312359]
```

## Response Format (Atom 1.0)

### Feed Elements

```xml
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/">
    <title>Search Results</title>
    <id>unique-query-id</id>
    <updated>2024-01-15T00:00:00Z</updated>
    <opensearch:totalResults>150</opensearch:totalResults>
    <opensearch:startIndex>0</opensearch:startIndex>
    <opensearch:itemsPerPage>10</opensearch:itemsPerPage>
    <entry>...</entry>
    <entry>...</entry>
</feed>
```

### Entry Elements

```xml
<entry>
    <id>http://arxiv.org/abs/2301.01234</id>
    <published>2023-01-15T12:00:00Z</published>
    <updated>2023-01-20T10:30:00Z</updated>
    <title>Paper Title</title>
    <summary>Abstract text...</summary>
    <author>
        <name>John Smith</name>
        <arxiv:affiliation>MIT</arxiv:affiliation>
    </author>
    <arxiv:comment>15 pages, 5 figures</arxiv:comment>
    <arxiv:journal_ref>Nature 123, 456 (2023)</arxiv:journal_ref>
    <arxiv:doi>10.1234/example</arxiv:doi>
    <arxiv:primary_category term="cs.AI"/>
    <category term="cs.AI"/>
    <category term="cs.LG"/>
    <link href="http://arxiv.org/abs/2301.01234" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2301.01234.pdf" rel="related" title="pdf" type="application/pdf"/>
</entry>
```

### Entry Fields Reference

| Element | Description |
|---------|-------------|
| `id` | arXiv abstract URL |
| `published` | First submission date (ISO 8601) |
| `updated` | Current version date |
| `title` | Paper title |
| `summary` | Abstract |
| `author/name` | Author name |
| `arxiv:affiliation` | Author affiliation |
| `arxiv:comment` | Author comments |
| `arxiv:journal_ref` | Journal reference |
| `arxiv:doi` | DOI identifier |
| `arxiv:primary_category` | Primary subject category |
| `category` | All subject categories |
| `link[@rel="alternate"]` | Abstract page URL |
| `link[@title="pdf"]` | PDF download URL |

## Subject Categories

### Computer Science (cs)

- `cs.AI` - Artificial Intelligence
- `cs.CL` - Computation and Language
- `cs.CV` - Computer Vision
- `cs.LG` - Machine Learning
- `cs.RO` - Robotics
- `cs.SE` - Software Engineering

### Physics

- `astro-ph` - Astrophysics
- `cond-mat` - Condensed Matter
- `hep-th` - High Energy Physics - Theory
- `quant-ph` - Quantum Physics

### Mathematics (math)

- `math.AG` - Algebraic Geometry
- `math.CO` - Combinatorics
- `math.ST` - Statistics Theory

### Other

- `q-bio` - Quantitative Biology
- `q-fin` - Quantitative Finance
- `stat` - Statistics
- `eess` - Electrical Engineering and Systems Science
- `econ` - Economics

Full list: https://arxiv.org/category_taxonomy

## Error Handling

Errors return Atom feeds with a single entry:

```xml
<feed>
    <entry>
        <title>Error</title>
        <summary>Error message here</summary>
        <link href="http://arxiv.org/help/api/user-manual.html"/>
    </entry>
</feed>
```

Common errors:
- Invalid query syntax
- Exceeded result limits
- Malformed date ranges

## Rate Limits

| Limit | Value |
|-------|-------|
| Max total results | 30,000 per query |
| Max per request | 2,000 results |
| Recommended delay | 3 seconds between calls |
| Update frequency | Daily at midnight |

## URL Encoding Reference

| Character | Encoding |
|-----------|----------|
| Space | `+` or `%20` |
| `:` | `%3A` |
| `(` | `%28` |
| `)` | `%29` |
| `"` | `%22` |
| `+` | `%2B` |
| `&` | `%26` |
| `=` | `%3D` |
| `?` | `%3F` |

## Example Queries

### Basic keyword search
```
http://export.arxiv.org/api/query?search_query=all:machine+learning&max_results=10
```

### Author search
```
http://export.arxiv.org/api/query?search_query=au:Hinton&max_results=20
```

### Category + date range
```
http://export.arxiv.org/api/query?search_query=cat:cs.AI+AND+submittedDate:[202301010000+TO+202312312359]&max_results=50
```

### Specific papers by ID
```
http://export.arxiv.org/api/query?id_list=2301.01234,2301.01235
```

### Complex boolean query
```
http://export.arxiv.org/api/query?search_query=%28au:smith+OR+au:jones%29+AND+ti:neural+network&sortBy=submittedDate&sortOrder=descending
```

## Attribution Requirements

When displaying arXiv data, include:

> "Data provided by arXiv.org"

Do not use arXiv brand name or logo without permission.

## Additional Resources

- arXiv API documentation: https://info.arxiv.org/help/api/
- Category taxonomy: https://arxiv.org/category_taxonomy
- Terms of use: https://info.arxiv.org/help/api/tou.html
