---
name: paper-reader
description: Read and extract text from academic papers. Use when the user wants to read a paper from arXiv, a PDF file, or a URL. Handles paper downloading and text extraction.
allowed-tools: Read, Bash
---

# Reading Academic Papers

This skill helps you read and extract content from academic papers.

## Supported Sources

1. **arXiv ID** - e.g., `2301.00001` or `arxiv:2301.00001`
2. **Local PDF** - e.g., `/path/to/paper.pdf`
3. **PDF URL** - e.g., `https://example.com/paper.pdf`

## Instructions

### For arXiv Papers

1. Extract the arXiv ID from the user's request (format: `YYMM.NNNNN`)
2. Run the download script:
   ```bash
   python claude_skills/paper-reader/scripts/download_paper.py arxiv <arxiv_id>
   ```
3. The script outputs the path to the downloaded PDF and extracted text

### For Local PDFs

1. Verify the file exists using Read tool
2. Run the extraction script:
   ```bash
   python claude_skills/paper-reader/scripts/download_paper.py local <path_to_pdf>
   ```

### For PDF URLs

1. Run the download script:
   ```bash
   python claude_skills/paper-reader/scripts/download_paper.py url <pdf_url>
   ```

## Output Format

The script returns JSON with:
- `title`: Paper title (if detectable)
- `source`: Original source (arXiv ID, path, or URL)
- `pdf_path`: Local path to the PDF
- `text`: Full extracted text
- `pages`: Number of pages
- `sections`: Detected sections with their content

## After Reading

Once you have the paper content, you can:
- Summarize it (see paper-summarizer skill)
- Analyze methodology and contributions (see paper-analyzer skill)
- Generate reproduction code (see paper-reproducer skill)

## Tips

- For long papers, focus on Abstract, Introduction, Method, and Conclusion sections first
- arXiv papers often have cleaner text extraction than scanned PDFs
- If text extraction fails, inform the user and suggest alternative sources
