import io
import os
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
from typing import Tuple
import tempfile


class FileProcessor:
    ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/jpg", "image/webp"}
    ALLOWED_PDF_TYPES = {"application/pdf"}
    MAX_FILE_SIZE = 10 * 1024 * 1024
    
    @staticmethod
    def validate_file(content_type: str, file_size: int) -> Tuple[bool, str]:
        if file_size > FileProcessor.MAX_FILE_SIZE:
            return False, "File size exceeds 10MB limit"
        
        all_allowed = FileProcessor.ALLOWED_IMAGE_TYPES | FileProcessor.ALLOWED_PDF_TYPES
        if content_type not in all_allowed:
            return False, f"Unsupported file type: {content_type}. Allowed: images (JPEG, PNG, WebP) and PDF"
        
        return True, "Valid file"
    
    @staticmethod
    def extract_text_from_image(image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            text = pytesseract.image_to_string(image, lang='eng+hin')
            
            text = ' '.join(text.split())
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_bytes: bytes) -> str:
        try:
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PdfReader(pdf_file)
            
            text_parts = []
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    # Preserve structure with page separators
                    text_parts.append(f"[Page {page_num + 1}]\n{page_text}")

            # Join with clear separation, preserving newlines
            full_text = '\n\n'.join(text_parts)

            # Clean up excessive whitespace but preserve paragraph structure
            lines = full_text.split('\n')
            cleaned_lines = [line.strip() for line in lines if line.strip()]
            full_text = '\n'.join(cleaned_lines)

            return full_text.strip()
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    @staticmethod
    def process_file(file_bytes: bytes, content_type: str) -> str:
        if content_type in FileProcessor.ALLOWED_IMAGE_TYPES:
            return FileProcessor.extract_text_from_image(file_bytes)
        elif content_type in FileProcessor.ALLOWED_PDF_TYPES:
            return FileProcessor.extract_text_from_pdf(file_bytes)
        else:
            raise ValueError(f"Unsupported content type: {content_type}")
