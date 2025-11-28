from pydantic import BaseModel
from typing import List, Literal


class BillItem(BaseModel):
    item_name: str
    item_amount: float
    item_rate: float
    item_quantity: float


class PageLineItems(BaseModel):
    page_no: str
    page_type: Literal["Bill Detail", "Final Bill", "Pharmacy"]
    bill_items: List[BillItem]


class TokenUsage(BaseModel):
    total_tokens: int
    input_tokens: int
    output_tokens: int


class ExtractedData(BaseModel):
    pagewise_line_items: List[PageLineItems]
    total_item_count: int


class ExtractBillRequest(BaseModel):
    document: str | None = None  # URL of the document (optional if file uploaded)


class ExtractBillResponse(BaseModel):
    is_success: bool
    token_usage: TokenUsage
    data: ExtractedData
