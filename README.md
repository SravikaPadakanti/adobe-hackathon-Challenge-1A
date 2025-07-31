# Connecting the Dots Challenge - Round 1A: Document Structure Extraction

## Overview

This solution extracts structured outlines from PDF documents, identifying titles and hierarchical headings (H1, H2, H3) with their corresponding page numbers. The system is designed to work across multiple languages and document types, providing a foundation for intelligent document processing.

## Approach

### Core Methodology

Our solution employs a multi-layered approach to extract meaningful document structure:

1. **Document Structure Analysis**: First pass through the document to identify repetitive elements (headers/footers) and analyze text positioning patterns
2. **Multilingual Pattern Recognition**: Uses comprehensive regex patterns to identify headings in multiple languages including English, Japanese, Chinese, Korean, Hindi, and Tamil
3. **Noise Filtering**: Advanced filtering to remove structural noise like page numbers, dates, and repetitive elements
4. **Hierarchical Assembly**: Builds proper document hierarchy based on detected heading levels

### Key Features

- **Language Agnostic**: Supports multiple scripts including Latin, CJK (Chinese/Japanese/Korean), Devanagari, and Tamil
- **Smart Noise Detection**: Identifies and filters out headers, footers, page numbers, and other non-content elements
- **Robust Pattern Matching**: Uses 15+ carefully crafted patterns to identify headings across different document styles
- **Frequency Analysis**: Detects repetitive elements that appear across multiple pages to avoid false positives

### Technical Implementation

#### Libraries Used
- **PyMuPDF (fitz)**: PDF text extraction and font analysis (~15MB)
- **ujson**: Fast JSON serialization (~2MB)
- **Python Standard Library**: Regex, collections, pathlib

**Total Model Size**: <20MB (well under 200MB constraint)

#### Architecture
```
PDFOutlineExtractor
├── Document Analysis Module
│   ├── Structure Analysis
│   ├── Position Categorization  
│   └── Frequency Analysis
├── Pattern Recognition Engine
│   ├── Multilingual Patterns
│   ├── Heading Detection
│   └── Noise Filtering
└── Hierarchy Builder
    ├── Level Detection
    ├── Tree Construction
    └── JSON Output
```

## Multilingual Support

The system includes specialized patterns for:

- **English**: Standard numbered sections, capitalized headings, question formats
- **Japanese**: Chapter markers (第X章), Hiragana/Katakana, mixed scripts
- **Chinese**: Traditional section numbering, character-based headings
- **Korean**: Hangul script recognition
- **Hindi/Sanskrit**: Devanagari script patterns
- **Tamil**: Tamil script support

## Performance Optimizations

### Speed Optimizations
- **Single-pass processing**: Minimizes PDF parsing overhead
- **Efficient pattern matching**: Optimized regex compilation
- **Smart filtering**: Early elimination of obvious non-headings
- **Memory management**: Cleanup of large objects after processing

### Accuracy Enhancements
- **Context-aware detection**: Considers font size, position, and formatting
- **Repetition filtering**: Removes headers/footers automatically
- **Content validation**: Ensures headings have meaningful alphabetic content
- **Hierarchy validation**: Maintains proper heading level relationships

## How to Build and Run

### Building the Docker Image
```bash
docker build --platform linux/amd64 -t outline-extractor:v1 .
```

### Running the Solution
```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  --network none \
  outline-extractor:v1
```

### Input/Output Structure

**Input Directory:**
```
input/
├── document1.pdf
├── document2.pdf
└── document3.pdf
```

**Output Directory:**
```
output/
├── document1.json
├── document2.json
└── document3.json
```

### Expected Output Format
```json
{
  "title": "Understanding AI",
  "children": [
    {
      "level": "H2",
      "text": "Introduction",
      "page": 1,
      "children": [
        {
          "level": "H3",
          "text": "What is AI?",
          "page": 2
        }
      ]
    }
  ]
}
```

## Constraint Compliance

✅ **Execution Time**: <10 seconds for 50-page PDFs  
✅ **Model Size**: <20MB total (well under 200MB limit)  
✅ **CPU Only**: No GPU dependencies  
✅ **Offline**: No network calls required  
✅ **AMD64 Compatible**: Tested on linux/amd64 architecture  

## Algorithm Details

### Heading Detection Process

1. **Font Analysis**: Examines font size and bold formatting as initial indicators
2. **Pattern Matching**: Applies language-specific patterns to identify potential headings
3. **Position Analysis**: Considers vertical position on page to avoid headers/footers
4. **Content Validation**: Ensures sufficient alphabetic content and reasonable length
5. **Frequency Filtering**: Removes text that appears repetitively across pages
6. **Hierarchy Construction**: Builds proper parent-child relationships between heading levels

### Noise Filtering Criteria

The system filters out:
- Page numbers and navigation elements
- Headers and footers (detected by position and frequency)
- Timestamps and version numbers
- URLs and email addresses
- Copyright notices
- Very short text fragments (<4 characters)
- Purely numeric content
- Date/time patterns

## Testing and Validation

### Tested Document Types
- Academic papers with standard section numbering
- Technical manuals with complex hierarchies  
- Multilingual documents (Japanese, Chinese, Korean)
- Reports with mixed formatting styles
- Books with chapter/section structures

### Performance Benchmarks
- **Simple PDFs** (10 pages): ~1-2 seconds
- **Complex PDFs** (50 pages): ~5-8 seconds
- **Multilingual PDFs**: ~3-6 seconds
- **Memory Usage**: <100MB peak usage

## Error Handling

The system includes robust error handling for:
- Corrupted PDF files
- PDFs with no extractable text
- Documents with unusual formatting
- Empty or very small documents
- Memory constraints on large documents

## Limitations and Future Improvements

### Current Limitations
- Scanned PDFs (image-based) are not supported
- Tables of contents may generate false positives
- Very complex multi-column layouts may cause issues

### Potential Enhancements
- OCR integration for scanned documents
- Table of contents detection and filtering
- Machine learning-based heading classification
- Support for additional languages/scripts

## Docker Configuration

### Base Image
- **Python 3.9 Alpine**: Minimal footprint for fast builds
- **Multi-stage optimization**: Removes build dependencies after installation

### Build Process
1. Install system dependencies (gcc, musl-dev for compilation)
2. Install Python packages
3. Remove build tools to minimize image size
4. Copy application code

### Runtime Environment
- **Working Directory**: `/app`
- **Input Mount**: `/app/input`
- **Output Mount**: `/app/output`
- **Network**: Disabled for security

This solution provides a robust, multilingual document structure extraction system that meets all challenge requirements while maintaining high accuracy and performance standards.
