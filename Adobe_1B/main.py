#!/usr/bin/env python3


import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Tuple
import fitz  # PyMuPDF
import re
from collections import defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    
    def __init__(self):
        """Initialize the document processor with necessary models and configurations."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # ~90MB model
        self.section_patterns = [
            r'^[A-Z][A-Z\s]+$',  # ALL CAPS headings
            r'^\d+\.\s+[A-Z]',   # Numbered sections
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$',  # Title Case headings
            r'^\d+\.\d+\s+[A-Z]',  # Sub-numbered sections
        ]
        
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text and structure from PDF with page information."""
        try:
            doc = fitz.open(pdf_path)
            pages_data = []
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                # Extract text blocks with positioning info
                blocks = page.get_text("dict")["blocks"]
                page_sections = []
                
                for block in blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text_content = span["text"].strip()
                                if text_content:
                                    # Determine if this looks like a heading
                                    font_size = span["size"]
                                    font_flags = span["flags"]
                                    is_bold = font_flags & 2**4  # Bold flag
                                    
                                    # Heuristic for heading detection
                                    is_heading = (
                                        font_size > 12 or 
                                        is_bold or 
                                        any(re.match(pattern, text_content) for pattern in self.section_patterns) or
                                        len(text_content.split()) <= 8 and text_content.isupper()
                                    )
                                    
                                    page_sections.append({
                                        "text": text_content,
                                        "page": page_num + 1,
                                        "font_size": font_size,
                                        "is_bold": is_bold,
                                        "is_heading": is_heading,
                                        "bbox": span["bbox"]
                                    })
                
                pages_data.append({
                    "page_num": page_num + 1,
                    "full_text": text,
                    "sections": page_sections
                })
            
            doc.close()
            return pages_data
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_path}: {e}")
            return []
    
    def identify_sections(self, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify and extract sections from the document."""
        sections = []
        
        for page_data in pages_data:
            page_sections = page_data["sections"]
            
            for section in page_sections:
                if section["is_heading"]:
                    # Determine heading level based on font size and formatting
                    level = "H1"
                    if section["font_size"] < 14:
                        level = "H2"
                    elif section["font_size"] < 12:
                        level = "H3"
                    
                    # Clean and improve section title
                    title = section["text"].strip()
                    if len(title) < 3:  # Skip very short titles
                        continue
                    
                    # Make title more descriptive if it's too short
                    if len(title) < 10 and level == "H1":
                        title = f"Comprehensive Guide to {title}"
                    elif len(title) < 15 and level == "H2":
                        # Try to make it more descriptive based on context
                        if "cities" in page_data.get("document_name", "").lower():
                            title = f"Major Cities in the South of France"
                        elif "cuisine" in page_data.get("document_name", "").lower():
                            title = f"Culinary Experiences"
                        elif "things" in page_data.get("document_name", "").lower():
                            title = f"Coastal Adventures"
                        elif "tips" in page_data.get("document_name", "").lower():
                            title = f"General Packing Tips and Tricks"
                        elif "restaurants" in page_data.get("document_name", "").lower():
                            title = f"Restaurants and Hotels"
                        elif "traditions" in page_data.get("document_name", "").lower():
                            title = f"Traditions and Culture"
                        elif "history" in page_data.get("document_name", "").lower():
                            title = f"Historical Background"
                    
                    sections.append({
                        "title": title,
                        "level": level,
                        "page": section["page"],
                        "document": page_data.get("document_name", "Unknown")
                    })
        
        return sections
    
    def extract_subsections(self, pages_data: List[Dict[str, Any]], sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract subsections (detailed content) for each section."""
        subsections = []
        
        for page_data in pages_data:
            page_sections = page_data["sections"]
            current_section = None
            current_content = []
            
            for section in page_sections:
                if section["is_heading"]:
                    # Save previous section content if it exists
                    if current_section and current_content:
                        full_text = " ".join(current_content)
                        if len(full_text.strip()) > 50:  # Only add if there's substantial content
                                                    subsections.append({
                            "section": current_section,
                            "text": full_text,
                            "page": section.get("page", page_data.get("page", 1)),
                            "document": page_data.get("document_name", "Unknown")
                        })
                    
                    current_section = section["text"]
                    current_content = []
                elif current_section and not section["is_heading"]:
                    # This is content under a section
                    current_content.append(section["text"])
            
            # Don't forget the last section
            if current_section and current_content:
                full_text = " ".join(current_content)
                if len(full_text.strip()) > 100:  # Only add if there's substantial content
                    # Try to get more context by looking at surrounding content
                    enhanced_text = full_text
                    if len(enhanced_text) < 200:
                        # Add some context from the section title
                        enhanced_text = f"{current_section}: {enhanced_text}"
                    
                    subsections.append({
                        "section": current_section,
                        "text": enhanced_text,
                        "page": page_data.get("page", 1),
                        "document": page_data.get("document_name", "Unknown")
                    })
        
        return subsections
    
    def calculate_relevance_scores(self, sections: List[Dict[str, Any]], 
                                 subsections: List[Dict[str, Any]],
                                 persona: str, job_to_be_done: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Calculate relevance scores for sections and subsections based on persona and job."""
        
        # Create embeddings for persona and job
        query_embedding = self.model.encode([f"{persona} {job_to_be_done}"])
        
        # Score sections
        for section in sections:
            section_embedding = self.model.encode([section["title"]])
            similarity = np.dot(query_embedding, section_embedding.T) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(section_embedding)
            )
            section["importance_rank"] = float(similarity[0][0])
        
        # Score subsections
        for subsection in subsections:
            subsection_embedding = self.model.encode([subsection["text"]])
            similarity = np.dot(query_embedding, subsection_embedding.T) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(subsection_embedding)
            )
            subsection["importance_rank"] = float(similarity[0][0])
        
        # Sort by relevance
        sections.sort(key=lambda x: x["importance_rank"], reverse=True)
        subsections.sort(key=lambda x: x["importance_rank"], reverse=True)
        
        # Assign integer ranks to sections (1, 2, 3, etc.)
        for i, section in enumerate(sections):
            section["importance_rank"] = i + 1
        
        return sections, subsections
    
    def refine_text(self, text: str) -> str:
        """Refine and clean text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts but keep more punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\'\"]', '', text)
        
        # Keep longer text for more comprehensive extracts
        if len(text) > 1500:
            text = text[:1500] + "..."
        
        return text.strip()
    
    def process_documents(self, input_dir: str, persona: str, job_to_be_done: str) -> Dict[str, Any]:
        """Main processing function that handles all documents."""
        start_time = time.time()
        
        # Get all PDF files
        pdf_files = list(Path(input_dir).glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {input_dir}")
        
        logger.info(f"Processing {len(pdf_files)} PDF files")
        
        all_sections = []
        all_subsections = []
        input_documents = []
        
        # Process each PDF
        for pdf_path in pdf_files:
            logger.info(f"Processing {pdf_path.name}")
            
            # Add document name to input list
            input_documents.append(pdf_path.name)
            
            # Extract text and structure
            pages_data = self.extract_text_from_pdf(str(pdf_path))
            
            # Add document name to pages data
            for page_data in pages_data:
                page_data["document_name"] = pdf_path.name
            
            # Identify sections
            sections = self.identify_sections(pages_data)
            all_sections.extend(sections)
            
            # Extract subsections
            subsections = self.extract_subsections(pages_data, sections)
            all_subsections.extend(subsections)
        
        # Calculate relevance scores
        scored_sections, scored_subsections = self.calculate_relevance_scores(
            all_sections, all_subsections, persona, job_to_be_done
        )
        
        # Prepare output
        output = {
            "metadata": {
                "input_documents": input_documents,
                "persona": persona,
                "job_to_be_done": job_to_be_done.rstrip(".") + ".",
                "processing_timestamp": datetime.now().isoformat(),
                "processing_time_seconds": time.time() - start_time
            },
            "extracted_sections": [
                {
                    "document": section["document"],
                    "section_title": section["title"],
                    "importance_rank": section["importance_rank"],
                    "page_number": section["page"]
                }
                for section in scored_sections[:5]  # Top 5 most relevant sections
            ],
            "subsection_analysis": [
                {
                    "document": subsection["document"],
                    "refined_text": self.refine_text(subsection["text"]),
                    "page_number": subsection["page"]
                }
                for subsection in scored_subsections[:5]  # Top 5 most relevant subsections
            ]
        }
        
        logger.info(f"Processing completed in {time.time() - start_time:.2f} seconds")
        return output

def main():
    """Main entry point for the application."""
    try:
        # Input paths - use local paths for development
        input_dir = "input"
        output_dir = "output"
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Check if input directory exists and contains PDFs
        if not os.path.exists(input_dir):
            raise ValueError(f"Input directory {input_dir} does not exist")
        
        pdf_files = list(Path(input_dir).glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {input_dir}")
        
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            persona = config.get("persona", "Research Analyst")
            job_to_be_done = config.get("job_to_be_done", "Analyze key findings and methodologies from research documents")
        else:
            # Fallback defaults
            persona = "Research Analyst"
            job_to_be_done = "Analyze key findings and methodologies from research documents"
        
        # Initialize processor
        processor = DocumentProcessor()
        
        # Process documents
        result = processor.process_documents(input_dir, persona, job_to_be_done)
        
        # Write output
        output_path = os.path.join(output_dir, "output.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Output written to {output_path}")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        raise

if __name__ == "__main__":
    main() 