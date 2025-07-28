import re
from pathlib import Path
import fitz  # PyMuPDF
import logging
import ujson  # Faster JSON library
from collections import Counter

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        # Multilingual & language-agnostic heading patterns
        self.patterns = [
            # English and numeric patterns
            (r"^[A-Z][a-z]+\s+[A-Z0-9IVX]+:?\s+[A-Za-z]{3,}.*", "H2"),
            (r"^\d+\.\s+[A-Z][a-zA-Z\s]{4,}.*", "H2"),
            (r"^\d+\.\d+\s+[A-Za-z]{4,}.*", "H3"),
            (r"^\d+\.\d+\.\d+\s+[A-Za-z]{4,}.*", "H4"),
            (r"^[A-Z][a-z]{3,}:\s*$", "H2"),
            (r"^[A-Z][A-Za-z\s&',-]{10,}:\s*$", "H3"),
            (r"^[A-Z][a-zA-Z\s]{8,}\?$", "H3"),
            (r"^[A-Z][A-Z\s&',-]{15,}$", "H2"),
            (r"^[A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}$", "H3"),

            # Japanese heading patterns
            (r"^第[一二三四五六七八九十百千\d]+章.*", "H2"),             # Chapter like 第1章
            (r"^[\u4e00-\u9faf]{2,10}$", "H2"),                         # Pure Kanji headings
            (r"^[\u3040-\u309f\u30a0-\u30ff]{3,}$", "H2"),           # Hiragana/Katakana
            (r"^[\u4e00-\u9faf\u3040-\u30ff\s]{4,}$", "H3"),         # Mixed Japanese scripts

            # Chinese (Simplified/Traditional)
            (r"^第[一二三四五六七八九十百千\d]+节.*", "H2"),             # Section headings
            (r"^[\u4e00-\u9fff]{2,10}$", "H2"),                         # Pure Chinese characters

            # Korean (Hangul)
            (r"^[\uac00-\ud7af\s]{3,}$", "H2"),                         # Hangul text (Korean script)

            # Devanagari (e.g., Hindi)
            (r"^[\u0900-\u097F\s]{4,}$", "H2"),                         # Hindi/Sanskrit heading pattern

            # Tamil
            (r"^[\u0B80-\u0BFF\s]{4,}$", "H2")                          # Tamil headings
        ]

        self.exclusion_patterns = [
            r"^Page\s+\d+\s+of\s+\d+$",
            r"^\d+\s+of\s+\d+$",
            r"^Page\s+\d+$",
            r"^\d{1,3}$",
            r"^[A-Za-z]{1,2}$",
            r"^\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4}$",
            r"^\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?$",
            r"^Version\s+[\d\.]+$",
            r"^©.*$",
            r"^\s*$",
            r"^[^\w\s]*$",
            r"^www\.|@|\.com|\.org|\.net",
            r"^\d+(?:\.\d+)*\s*%?$",
            r"^[A-Z]{2,}\s+\d{1,2},?\s+\d{4}$",
            r"^\w+\s+\d{1,2},?\s+\d{4}$",
        ]

        self.text_frequency = Counter()
        self.page_positions = {}
        self.seen_headings = set()

    def analyze_document_structure(self, doc):
        """Analyze document to identify repetitive elements and page structure"""
        self.text_frequency.clear()
        self.page_positions.clear()
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_height = page.rect.height
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    block_y = block.get("bbox", [0, 0, 0, 0])[1]  # y-coordinate
                    position_category = self.categorize_position(block_y, page_height)
                    
                    for line in block["lines"]:
                        line_text = ""
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                        
                        text = line_text.strip()
                        if text and len(text) > 1:
                            self.text_frequency[text] += 1
                            if text not in self.page_positions:
                                self.page_positions[text] = []
                            self.page_positions[text].append((page_num, position_category))

    def categorize_position(self, y_coord, page_height):
        """Categorize text position on page (header, body, footer)"""
        relative_pos = y_coord / page_height
        if relative_pos < 0.15:
            return "header"
        elif relative_pos > 0.85:
            return "footer"
        else:
            return "body"

    def is_repetitive_element(self, text):
        """Check if text appears frequently across pages (likely header/footer)"""
        if text not in self.text_frequency:
            return False
            
        frequency = self.text_frequency[text]
        positions = self.page_positions.get(text, [])
        
        # If appears on many pages, likely repetitive
        if frequency > 2:
            # Check if consistently in header/footer positions
            position_types = [pos[1] for pos in positions]
            if position_types.count("header") > 1 or position_types.count("footer") > 1:
                return True
                
        return False

    def is_structural_noise(self, text):
        """Identify text that's likely structural noise rather than content"""
        # Very short text
        if len(text.strip()) < 4:
            return True
            
        # Only numbers or simple patterns
        if re.match(r'^[\d\s\-\.\,\/]+$', text):
            return True
            
        # Check against exclusion patterns
        for pattern in self.exclusion_patterns:
            if re.match(pattern, text, re.IGNORECASE):
                return True
                
        return False

    def has_heading_characteristics(self, text, font_info=None):
        """Determine if text has characteristics typical of headings"""
        # Must have substantial alphabetic content
        alpha_count = sum(1 for c in text if c.isalpha())
        if alpha_count < 3:
            return False
            
        # Should not be mostly numbers or punctuation
        non_alpha_count = len(text) - alpha_count
        if non_alpha_count > alpha_count:
            return False
            
        # Check for balanced structure (not just random text)
        words = text.split()
        if len(words) == 1 and len(text) > 30:  # Very long single word
            return False
            
        # Should not contain too many special characters relative to length
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if len(text) > 5 and special_chars / len(text) > 0.3:
            return False
            
        return True

    def extract_title_from_pdf(self, doc):
        """Extract document title from metadata or first meaningful line"""
        metadata = doc.metadata
        if metadata.get('title') and len(metadata['title'].strip()) > 5:
            return metadata['title'].strip()
            
        # Look for title in first few pages
        for page_num in range(min(3, len(doc))):
            text = doc[page_num].get_text()
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            for line in lines[:10]:
                if (len(line) > 10 and 
                    not self.is_structural_noise(line) and
                    not re.match(r'^\d+\.', line) and
                    self.has_heading_characteristics(line)):
                    return line
                    
        return "Untitled Document"

    def extract_outline(self, pdf_path):
        """Extract hierarchical outline from PDF"""
        doc = fitz.open(pdf_path)
        
        # First pass: analyze document structure
        self.analyze_document_structure(doc)
        
        title = self.extract_title_from_pdf(doc)
        outline = {"title": title, "children": []}
        current_level = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text_dict = page.get_text("dict")
            
            for block in text_dict.get("blocks", []):
                if "lines" in block:
                    for line in block["lines"]:
                        line_text = ""
                        font_size = 0
                        is_bold = False
                        
                        for span in line.get("spans", []):
                            line_text += span.get("text", "")
                            font_size = max(font_size, span.get("size", 0))
                            flags = span.get("flags", 0)
                            if flags & 2**4:  # Bold flag
                                is_bold = True

                        text = line_text.strip()
                        
                        # Skip if structural noise or repetitive
                        if (self.is_structural_noise(text) or 
                            self.is_repetitive_element(text) or
                            not self.has_heading_characteristics(text)):
                            continue

                        level = self.detect_level(text)
                        if level and text not in self.seen_headings:
                            heading = {
                                "level": level,
                                "text": text,
                                "page": page_num + 1,
                                "children": []
                            }

                            self.seen_headings.add(text)

                            # Build hierarchy
                            while (current_level and 
                                   self._get_level_weight(current_level[-1]["level"]) >= 
                                   self._get_level_weight(level)):
                                current_level.pop()

                            if current_level:
                                current_level[-1]["children"].append(heading)
                            else:
                                outline["children"].append(heading)

                            current_level.append(heading)

        doc.close()
        return outline

    def detect_level(self, text):
        """Detect heading level based on patterns"""
        for pattern, level in self.patterns:
            if re.match(pattern, text):
                return level
        return None

    def _get_level_weight(self, level):
        """Get numeric weight for heading level"""
        return {"H1": 1, "H2": 2, "H3": 3, "H4": 4}.get(level, float("inf"))

def main():
    """Main function to process PDFs"""
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)

    extractor = PDFOutlineExtractor()
    pdf_files = list(input_dir.glob("*.pdf"))

    if not pdf_files:
        logger.warning("No PDF files found in input directory")
        return

    for pdf_file in pdf_files:
        try:
            logger.info(f"Processing {pdf_file.name}...")
            result = extractor.extract_outline(str(pdf_file))
            
            # Clean up result - remove empty children arrays
            def clean_outline(node):
                if isinstance(node, dict):
                    if "children" in node and not node["children"]:
                        del node["children"]
                    else:
                        for child in node.get("children", []):
                            clean_outline(child)
                elif isinstance(node, list):
                    for item in node:
                        clean_outline(item)
            
            clean_outline(result)
            
            output_file = output_dir / f"{pdf_file.stem}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                ujson.dump(result, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved outline to {output_file.name}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {str(e)}")

if __name__ == "__main__":
    main()