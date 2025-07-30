PDF Outline Extractor: A Deep Dive
This repository provides a powerful command-line tool designed to analyze PDF documents and automatically generate a structured, hierarchical outline. It transforms unstructured content into a clean, machine-readable JSON format, perfect for content analysis, data ingestion, or building document navigation features.

The script intelligently identifies titles, headings, and subheadings by analyzing text properties, making it effective even on PDFs that lack a built-in table of contents.

✨ Core Features
Intelligent Heading Detection: Uses a heuristic-based approach to find headings by analyzing font size, weight (bold), and style.

Hierarchical Structuring: Automatically clusters headings into levels (H1, H2, H3, etc.) to represent the document's structure accurately.

Built-in TOC Fallback: For perfectly structured PDFs, it will first attempt to use the embedded bookmarks for a flawless outline.

Noise Reduction: Actively filters out irrelevant text like page numbers, headers, footers, and URLs to keep the outline clean.

Batch Processing: Processes all PDF files placed in the input directory in a single run.

Containerized & Portable: Comes with a Dockerfile for easy, dependency-free execution on any system with Docker, ensuring consistent results.

🚀 Getting Started: A Step-by-Step Guide
Follow these instructions to set up and run the extractor.

Step 1: System Prerequisites
Ensure you have the following software installed on your machine:

Python (Version 3.9 or newer)

Git (for cloning the repository)

Docker (optional, for containerized execution)

Step 2: Clone & Prepare the Project
Open your terminal and run the following commands to download the project and navigate into the directory.

Bash

git clone <your-repo-url>
cd ADOBE_HACKATHON
Step 3: Choose Your Execution Method
You can run the extractor directly on your machine or inside a Docker container.

PATH A: Local Environment Execution (Recommended for Development)
This method gives you more control for testing and modifications.

Create a Virtual Environment: This isolates the project's dependencies from your system's Python.

Bash

# Create the environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows (PowerShell):
venv\Scripts\activate
Install Dependencies: This command installs all the required Python libraries listed in requirements.txt.

Bash

pip install --no-cache-dir -r requirements.txt
Add Your Files: Place one or more PDF files into the input/ directory.

Run the Extractor: Execute the main script.

Bash

python process_pdf.py
The script will process each PDF and save the corresponding JSON outline in the output/ directory.

PATH B: Docker Container Execution (Recommended for Production/Portability)
This is the simplest way to run the tool without worrying about Python versions or dependencies.

Add Your Files: Place your PDFs into the input/ directory.

Build the Docker Image: This command packages the application and its environment into a reusable image named outline-extractor.

Bash

docker build -t outline-extractor .
Run the Container: This command starts the container, processes the files, and then automatically removes itself.

Bash

docker run --rm \
  -v "${PWD}/input:/app/input" \
  -v "${PWD}/output:/app/output" \
  outline-extractor
Explanation: The -v flags mount your local input and output folders into the container. This allows the container to read your PDFs and write the JSON files back to your machine.

Windows Users: Use %cd% instead of ${PWD} in Command Prompt.

⚙️ How It Works: The Extraction Pipeline
The tool follows a multi-stage process to ensure the highest quality outlines:

Bookmark Priority: It first checks if the PDF has a built-in table of contents (bookmarks). If present, it uses this data for a perfect outline and skips the heuristic analysis.

Text Block Parsing: If no bookmarks are found, it uses the PyMuPDF library to parse every page. It extracts text blocks along with their metadata: font size, font name, bold/italic flags, and coordinates on the page.

Heuristic Scoring: Each text block is assigned a "heading score". Blocks with larger fonts, bold styling, or that match common heading keywords (e.g., "Introduction," "Conclusion," "Appendix") receive higher scores.

Dynamic Clustering: Instead of using fixed font sizes for heading levels, the script analyzes all the font sizes present in the document. It identifies the largest "gaps" between font sizes to dynamically determine which sizes correspond to H1, H2, H3, and H4 levels.

Refinement & Filtering: The script cleans the list of potential headings by:

Removing lines that look like URLs or contact information.

Discarding text that is too close in size to the main body font.

Collapsing duplicate headings that may appear in page headers or footers.

Final Output: The cleaned, sorted, and structured list of headings is compiled into the final JSON output.

📋 Understanding the Output Schema
Each processed PDF will generate a <filename>.json file in the output/ directory with the following structure:

JSON

{
  "title": "<The main document title>",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter 1: The First Heading",
      "page": 0
    },
    {
      "level": "H2",
      "text": "A subheading within Chapter 1",
      "page": 1
    }
  ]
}
"title": The primary title of the document, typically the highest-ranking heading found on the first page.

"outline": An ordered array of heading objects.

"level": The detected hierarchical level (H1, H2, etc.).

"text": The clean text content of the heading.

"page": The zero-based page number where the heading was found.

