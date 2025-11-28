import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from typing import Optional
from dotenv import load_dotenv

from app.models import (
    ExtractBillResponse,
    TokenUsage,
    ExtractedData
)
from app.document_processor import process_document, process_uploaded_file
from app.llm_service import LLMService

load_dotenv()

app = FastAPI(title="Bill Extraction API", version="1.0.0")


@app.post("/extract-bill-data", response_model=ExtractBillResponse)
async def extract_bill_data(
    file: Optional[UploadFile] = File(None),
    document: Optional[str] = Form(None)
):
    """
    Extract line items from a bill/invoice.
    Accepts either:
    - file: Direct file upload (PDF/image)
    - document: URL to the document
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Google API key not configured")

        # Process based on input type
        if file:
            content = await file.read()
            image_bytes_list = process_uploaded_file(content, file.filename or "")
        elif document:
            image_bytes_list = await process_document(document)
        else:
            raise HTTPException(status_code=400, detail="Provide either 'file' or 'document' URL")

        # Extract data using LLM
        llm_service = LLMService(api_key)
        pagewise_items = llm_service.extract_from_images(image_bytes_list)

        total_items = sum(len(page.bill_items) for page in pagewise_items)
        token_usage = llm_service.get_token_usage()

        return ExtractBillResponse(
            is_success=True,
            token_usage=TokenUsage(**token_usage),
            data=ExtractedData(
                pagewise_line_items=pagewise_items,
                total_item_count=total_items
            )
        )

    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
