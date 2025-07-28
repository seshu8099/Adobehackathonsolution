# Approach Explanation: Persona-Driven Document Intelligence

## Methodology Overview

Our solution implements a multi-stage document intelligence system that combines traditional PDF parsing techniques with modern semantic understanding to deliver persona-specific insights. The approach is designed to be both computationally efficient and semantically accurate while operating within strict constraints.

## Core Design Philosophy

The system follows a "extract, understand, rank" pipeline that prioritizes:
1. **Robust extraction** of document structure and content
2. **Semantic understanding** of user intent and document relevance
3. **Intelligent ranking** based on persona-job alignment

## Technical Implementation

### Stage 1: Document Structure Extraction

We employ PyMuPDF (fitz) for its superior text extraction capabilities, particularly its ability to preserve formatting metadata. The extraction process captures:
- Text content with positioning information
- Font properties (size, weight, style)
- Spatial relationships between text elements
- Page-level organization

This approach ensures we maintain the document's structural integrity while extracting meaningful content.

### Stage 2: Intelligent Section Detection

Our section detection algorithm combines multiple heuristics to identify headings reliably:
- **Font-based detection**: Larger font sizes (>12pt) and bold formatting indicate headings
- **Pattern matching**: Regex patterns identify numbered sections, title case, and ALL CAPS headings
- **Contextual analysis**: Short, prominent text blocks are flagged as potential headings

This multi-faceted approach handles diverse document formats without relying on hardcoded assumptions.

### Stage 3: Semantic Relevance Scoring

We leverage the `all-MiniLM-L6-v2` sentence transformer model for semantic similarity calculations. This model:
- Provides high-quality embeddings in a compact 90MB package
- Enables fast similarity computations on CPU
- Maintains semantic accuracy across diverse domains

The scoring process creates embeddings for both the persona-job combination and individual document sections/subsections, then calculates cosine similarity to determine relevance.

### Stage 4: Content Refinement and Ranking

The system implements intelligent content processing:
- **Text cleaning**: Removes PDF artifacts and normalizes whitespace
- **Length optimization**: Truncates subsections to 500 characters for readability
- **Ranked selection**: Returns top 20 sections and top 30 subsections by relevance

## Key Innovations

### Adaptive Persona Understanding
Rather than using fixed templates, the system dynamically interprets persona-job combinations through semantic embedding, allowing it to handle diverse use cases from academic research to business analysis.

### Multi-level Content Analysis
The solution operates at both section and subsection levels, providing both high-level structure and detailed content insights. This hierarchical approach ensures comprehensive coverage of relevant information.

### Constraint-Aware Optimization
Every design decision considers the 60-second time limit and 1GB model size constraint:
- Model selection prioritizes speed and size over maximum accuracy
- Processing pipeline minimizes redundant computations
- Memory usage is optimized through efficient data structures

## Performance Characteristics

The solution is designed to scale efficiently:
- **Linear time complexity** with document count
- **Constant memory usage** regardless of document size
- **Parallel processing** where possible within CPU constraints

## Robustness Features

- **Error handling**: Graceful degradation for corrupted or unreadable PDFs
- **Format flexibility**: Handles various PDF structures and formatting styles
- **Domain agnostic**: Works across academic, business, and technical documents

This approach balances computational efficiency with semantic accuracy, delivering intelligent document analysis that adapts to user needs while respecting system constraints. 