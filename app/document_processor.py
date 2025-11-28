import httpx
import fitz  # PyMuPDF
from PIL import Image
import io
import base64
from typing import List


async def download_document(url: str) -> bytes:
    """Download document from URL."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.content


def pdf_to_images(pdf_bytes: bytes) -> List[bytes]:
    """Convert PDF pages to images."""
    images = []
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        # Render at 2x resolution for better OCR
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        images.append(img_bytes)
    
    doc.close()
    return images


def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_bytes).decode("utf-8")


async def process_document(url: str) -> List[bytes]:
    """
    Download and process document, returning list of image bytes.
    Handles both PDFs and direct images.
    """
    content = await download_document(url)
    
    # Check if it's a PDF
    if content[:4] == b'%PDF' or url.lower().endswith('.pdf'):
        return pdf_to_images(content)
    else:
        # It's an image, return as single item list
        return [content]


def process_uploaded_file(content: bytes, filename: str = "") -> List[bytes]:
    """
    Process uploaded file content, returning list of image bytes.
    Handles both PDFs and direct images.
    """
    # Check if it's a PDF
    if content[:4] == b'%PDF' or filename.lower().endswith('.pdf'):
        return pdf_to_images(content)
    else:
        # It's an image, return as single item list
        return [content]
