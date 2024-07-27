from pydantic import BaseModel


class RetranslateClipResponse(BaseModel):
    llm_response: str
    "Textual output produced by the LLM"
