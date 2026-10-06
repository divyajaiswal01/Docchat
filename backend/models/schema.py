from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    document_id: str
    filename: str
    page_count: int
    char_count: int


class ChatRequest(BaseModel):
    document_id: str
    question: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    answer: str


class ErrorResponse(BaseModel):
    error: bool = True
    message: str
