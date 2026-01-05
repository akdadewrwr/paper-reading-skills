#!/usr/bin/env python3
"""Download and extract text from academic papers."""

import sys
import os
import json
import re
import tempfile
from pathlib import Path

import fitz  # PyMuPDF
import requests
import arxiv


def download_arxiv(arxiv_id: str, cache_dir: str) -> str:
    """Download a paper from arXiv."""
    # Clean up arxiv ID
    arxiv_id = arxiv_id.lower().replace("arxiv:", "").strip()

    cache_path = os.path.join(cache_dir, f"arxiv_{arxiv_id}.pdf")

    if os.path.exists(cache_path):
        return cache_path

    # Search for the paper
    search = arxiv.Search(id_list=[arxiv_id])
    results = list(search.results())

    if not results:
        raise ValueError(f"arXiv paper not found: {arxiv_id}")

    paper = results[0]
    paper.download_pdf(dirpath=cache_dir, filename=f"arxiv_{arxiv_id}.pdf")

    return cache_path


def download_url(url: str, cache_dir: str) -> str:
    """Download a PDF from a URL."""
    filename = url.split('/')[-1]
    if not filename.endswith('.pdf'):
        filename = f"{hash(url) & 0xFFFFFFFF}.pdf"

    cache_path = os.path.join(cache_dir, filename)

    if os.path.exists(cache_path):
        return cache_path

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    with open(cache_path, 'wb') as f:
        f.write(response.content)

    return cache_path


def extract_text(pdf_path: str) -> dict:
    """Extract text and metadata from a PDF."""
    doc = fitz.open(pdf_path)

    full_text = []
    sections = []
    current_section = {"title": "Beginning", "content": []}

    # Common section headers
    section_pattern = re.compile(
        r'^(?:\d+\.?\s*)?(abstract|introduction|related\s*work|background|'
        r'methodology|method|methods|approach|experiments?|results?|'
        r'discussion|conclusion|conclusions|references|acknowledgements?|appendix)',
        re.IGNORECASE
    )

    title = None

    for page_num, page in enumerate(doc):
        text = page.get_text()
        full_text.append(text)

        # Try to get title from first page
        if page_num == 0 and not title:
            lines = text.strip().split('\n')
            for line in lines[:5]:  # Check first 5 lines
                line = line.strip()
                if len(line) > 10 and len(line) < 200:
                    title = line
                    break

        # Identify sections
        for line in text.split('\n'):
            line_stripped = line.strip()
            match = section_pattern.match(line_stripped)
            if match:
                if current_section["content"]:
                    current_section["content"] = "\n".join(current_section["content"])
                    sections.append(current_section)
                current_section = {"title": line_stripped, "content": []}
            else:
                if line_stripped:
                    current_section["content"].append(line_stripped)

    # Add final section
    if current_section["content"]:
        current_section["content"] = "\n".join(current_section["content"])
        sections.append(current_section)

    num_pages = len(doc)
    doc.close()

    return {
        "title": title,
        "pdf_path": pdf_path,
        "pages": num_pages,
        "text": "\n\n".join(full_text),
        "sections": sections,
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: download_paper.py <arxiv|local|url> <source>"
        }))
        sys.exit(1)

    source_type = sys.argv[1].lower()
    source = sys.argv[2]

    cache_dir = os.path.join(tempfile.gettempdir(), "paper_cache")
    os.makedirs(cache_dir, exist_ok=True)

    try:
        if source_type == "arxiv":
            pdf_path = download_arxiv(source, cache_dir)
        elif source_type == "local":
            if not os.path.exists(source):
                raise ValueError(f"File not found: {source}")
            pdf_path = source
        elif source_type == "url":
            pdf_path = download_url(source, cache_dir)
        else:
            raise ValueError(f"Unknown source type: {source_type}")

        result = extract_text(pdf_path)
        result["source"] = source
        result["source_type"] = source_type

        print(json.dumps(result, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
