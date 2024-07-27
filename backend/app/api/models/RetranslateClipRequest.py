from pydantic import BaseModel


class RetranslateClipRequest(BaseModel):
    use_mae: bool
    "Should the MAE embeddings be used during translation?"
    
    use_dino: bool
    "Should the DINO embeddings be used during translation?"

    use_sign2vec: bool
    "Should the Sign2Vec embeddings be used during translation?"

    prompt: str
    "The user prompt to give to the LLM (including any context and such)"
