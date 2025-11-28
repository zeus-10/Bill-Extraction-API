import json
import google.generativeai as genai
from PIL import Image
import io
from typing import List, Dict
from app.models import PageLineItems, BillItem


EXTRACTION_PROMPT = """You are an expert at extracting line item data from bills and invoices.

Analyze this bill/invoice image and extract ALL line items with their details.

For each page, identify:
1. Page type: "Bill Detail", "Final Bill", or "Pharmacy"
2. All line items with:
   - item_name: Exactly as written in the bill
   - item_amount: Net amount after discounts (float)
   - item_rate: Unit rate/price (float)
   - item_quantity: Quantity (float)

IMPORTANT:
- Extract EVERY line item, don't miss any
- Don't double count items
- Use 0.0 if rate or quantity is not mentioned
- item_amount should be the final amount for that line item

Return ONLY valid JSON in this exact format (no markdown, no code blocks):
{
    "page_type": "Bill Detail",
    "bill_items": [
        {
            "item_name": "string",
            "item_amount": 0.0,
            "item_rate": 0.0,
            "item_quantity": 0.0
        }
    ]
}
"""


class LLMService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.total_tokens = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def extract_from_image(self, image_bytes: bytes, page_no: int) -> PageLineItems:
        """Extract line items from a single image."""
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        response = self.model.generate_content(
            [EXTRACTION_PROMPT, image],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            )
        )

        # Track token usage
        if response.usage_metadata:
            self.input_tokens += response.usage_metadata.prompt_token_count
            self.output_tokens += response.usage_metadata.candidates_token_count
            self.total_tokens += response.usage_metadata.total_token_count

        # Parse response - clean up markdown if present
        content = response.text.strip()
        if content.startswith("```"):
            # Remove markdown code blocks
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        content = content.strip()
        
        data = json.loads(content)

        return PageLineItems(
            page_no=str(page_no),
            page_type=data.get("page_type", "Bill Detail"),
            bill_items=[BillItem(**item) for item in data.get("bill_items", [])]
        )

    def extract_from_images(self, image_bytes_list: List[bytes]) -> List[PageLineItems]:
        """Extract line items from multiple images."""
        results = []
        for idx, img_bytes in enumerate(image_bytes_list, start=1):
            page_data = self.extract_from_image(img_bytes, idx)
            results.append(page_data)
        return results

    def get_token_usage(self) -> Dict[str, int]:
        return {
            "total_tokens": self.total_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens
        }
