import numpy as np
from typing import List


class EmbeddingNeighborLookup:
    """
    Finds the one nearest text token for each given visual embedding.
    It uses dot-product similarity metric to find the most similar token.
    """

    def __init__(
        self,
        token_embeddings: np.ndarray,
        tokens: List[str]
    ):
        self.token_embeddings = token_embeddings
        "Matrix with the embedding vector for each text token"

        self.tokens = tokens
        "List of token strings ordered by their IDs"

        assert str(token_embeddings.dtype) == "float32"
        assert len(self.token_embeddings.shape) == 2
        assert len(self.tokens) == self.token_embeddings.shape[0]
    
    def find_neighbors_for(self, visual_embeddings: np.ndarray) -> List[str]:
        assert str(visual_embeddings.dtype) == "float32"
        assert len(visual_embeddings.shape) == 2
        assert visual_embeddings.shape[1] == self.token_embeddings.shape[1]
        
        similarities = self.token_embeddings @ visual_embeddings.T
        token_indices = similarities.argmax(axis=0)

        return [self.tokens[i] for i in token_indices]


if __name__ == "__main__":
    lookup = EmbeddingNeighborLookup(
        token_embeddings=np.empty(shape=(128_000, 4096), dtype=np.float32),
        tokens=[str(i) for i in range(128_000)]
    )
    visual_embeddings = np.empty(shape=(300, 4096), dtype=np.float32)
    
    neighbors = lookup.find_neighbors_for(visual_embeddings)
    print(neighbors)
