# Adobe Hackathon: Round 1A Outline Extractor

This repository contains a robust **Outline Extraction** tool for Adobe Hackathon Round 1A. It processes PDFs to extract a structured Table-of-Contents (TOC)–style JSON with document titles and hierarchical headings.

---

## 📁 Project Structure

```
ADOBE_HACKATHON/
├── input/                # Place your PDF files here (file01.pdf, file02.pdf, ...)
├── output/               # Generated JSON outlines will appear here
├── process_pdf.py        # Main extraction script
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container build instructions
└── README.md             # This documentation
```

---

## 🛠️ Prerequisites

* **Python 3.9+** installed locally (for development/testing).
* **Docker** (Desktop or Engine) for containerized builds and execution.

---

## 🚀 Installation & Local Execution

1. **Clone the repo** and navigate into it:

   ```bash
   git clone <your-repo-url>
   cd ADOBE_HACKATHON
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate   # Windows PowerShell
   ```

3. **Install Python dependencies**:

   ```bash
   pip install --no-cache-dir -r requirements.txt
   ```

4. **Place your PDFs** in the `input/` directory.

5. **Run the extraction**:

   ```bash
   python process_pdf.py
   ```

   * Processed JSON files will be written to `output/`.

---

## 🐳 Dockerized Execution

This tool is fully containerized for offline, CPU-only execution on Linux/amd64.

1. **Build the Docker image**:

   ```bash
   docker build -t outline-extractor .
   ```

2. **Run the container**:

   ```bash
   docker run --rm \
     -v "${PWD}/input:/app/input" \
     -v "${PWD}/output:/app/output" \
     outline-extractor
   ```

   * The container reads PDFs from `/app/input` and writes JSON to `/app/output`.

> **Note (Windows)**: In Command Prompt use `%cd%` instead of `${PWD}` for volume mounts.

---

## 🔍 How It Works

1. **TOC Fallback**: Attempts to use built-in PDF bookmarks (if present) for perfect outline.
2. **Heuristic Extraction**: Parses text blocks via PyMuPDF, capturing font size, style, and position.
3. **Scoring**: Assigns heading scores based on font-size, bold/italic flags, keyword patterns, and spatial cues.
4. **Dynamic Clustering**: Clusters font sizes into heading levels H1–H4 using a largest-gap algorithm.
5. **Filtering**: Removes URL/RSVP lines, hyphen-only blocks, and body-text–sized clusters too close to body font.
6. **Deduplication**: Collapses duplicate headings and orders them by page and position.

---

## ⚙️ Configuration

* **Score thresholds** and **delta sizes** can be fine-tuned in `process_pdf.py` constants (e.g., `DELTA_SIZE`, keyword regex patterns).
* **Max clusters** and **max text length** filters are adjustable to fit different document styles.

---

## 📋 Output Format

Each PDF produces `<filename>.json` with this schema:

```json
{
  "title": "<Document Title>",
  "outline": [
    { "level": "H1", "text": "Main Heading", "page": 0 },
    { "level": "H2", "text": "Subheading", "page": 1 },
    ...
  ]
}
```

* **`title`**: The top-level heading or PDF metadata title (page 0).
* **`outline`**: Ordered list of detected headings with hierarchical levels and zero-based page indices.

---

## 🚩 Contributing

Feel free to open issues or PRs if you discover edge-cases or have suggestions for improving scoring heuristics and clustering.

---

## 📜 License

This project is released under the **MIT License**. Feel free to adapt for your own use.
