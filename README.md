
Overview

This project addresses the Adobe India Hackathon Round 1A challenge by extracting structured outlines (title, H1, H2, H3 headings with page numbers) from diverse PDFs, including scanned, highly unstructured, and edge cases. It outputs JSON files, runs offline on a CPU (8 CPUs, 16GB RAM, AMD64), stays within 200MB, and processes 50 pages in ≤10s, with multilingual support for bonus points.

🛠 Features
🧠 Automatic heading detection based on patterns, position, and formatting

🔢 Supports multiple heading levels (H1, H2, H3, H4)

🧹 Filters out headers, footers, timestamps, page numbers, and other structural noise

🌐 Multilingual support:

✅ English

✅ Japanese (Kanji, Hiragana, Katakana)

✅ Chinese (Simplified and Traditional)

✅ Korean (Hangul)

✅ Hindi and other Devanagari scripts

✅ Tamil

⚙️ Fully containerized with Docker for easy execution

📤 Outputs results as a structured JSON outline

📂 Project Structure
graphql
Copy
Edit
.
├── Dockerfile             # Docker setup to containerize the app
├── extract_outline.py     # Main script to extract outlines from PDFs
├── requirements.txt       # Python dependencies
├── input/                 # Folder to place PDF files for processing
└── output/                # Folder where output JSON files will be saved
🐳 Running with Docker
1. 🏗️ Build the Docker image
bash
Copy
Edit
docker build -t pdf-outline-extractor .
2. 📥 Place your PDFs
Put your PDF files into a local input/ folder.

3. 🚀 Run the container
bash
Copy
Edit
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-outline-extractor
Input PDFs go in the input/ folder

JSON output will be saved in the output/ folder

🧪 Example Output
json
Copy
Edit
{
  "title": "Sample Document",
  "children": [
    {
      "level": "H2",
      "text": "1. Introduction",
      "page": 1,
      "children": [
        {
          "level": "H3",
          "text": "1.1 Purpose",
          "page": 1
        }
      ]
    }
  ]
}
📦 Python Dependencies
From requirements.txt:

graphql
Copy
Edit
pymupdf    # For parsing PDF content
ujson      # For fast JSON serialization
Install manually using:

bash
Copy
Edit
pip install -r requirements.txt

📑 Notes
Designed to handle diverse documents with mixed scripts

Accurate and noise-free outline generation

Can be extended with more language rules or custom heading patterns
