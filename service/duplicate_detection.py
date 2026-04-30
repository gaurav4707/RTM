import requests
import numpy as np
from typing import List, Dict, Any, Optional

class DuplicateDetector:
    """
    Detects semantically similar requirements using Ollama embeddings.
    Uses 'nomic-embed-text' model for vector generation.
    """
    
    def __init__(self, ollama_url: str = "http://localhost:11434/api/embeddings"):
        self.ollama_url = ollama_url
        self.model = "nomic-embed-text"

    def _get_embedding(self, text: str) -> np.ndarray:
        """Fetch embedding vector from Ollama."""
        try:
            response = requests.post(
                self.ollama_url,
                json={"model": self.model, "prompt": text},
                timeout=5
            )
            response.raise_for_status()
            return np.array(response.json()["embedding"])
        except Exception as e:
            # If Ollama is not running, we'll return a zero vector 
            # (or we could raise an error depending on desired behavior)
            print(f"Ollama embedding error: {e}")
            return np.zeros(768) # nomic-embed-text dimension is 768

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        if np.all(v1 == 0) or np.all(v2 == 0):
            return 0.0
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        return np.dot(v1, v2) / (norm1 * norm2)

    def check_description(self, description: str, existing_requirements: List[Dict[str, str]], threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        """
        Check a single new description against existing requirements.
        Returns the most similar match if it exceeds the threshold.
        """
        if not existing_requirements:
            return None

        new_embedding = self._get_embedding(description)
        best_match = None
        highest_score = 0.0

        for req in existing_requirements:
            existing_embedding = self._get_embedding(req['description'])
            score = self._cosine_similarity(new_embedding, existing_embedding)
            
            if score > highest_score:
                highest_score = score
                best_match = {
                    'req_id': req['id'],
                    'score': round(float(score), 4)
                }

        if highest_score > threshold:
            return best_match
        return None

    def find_top_matches(self, target_text: str, candidates: List[Dict[str, str]], top_n: int = 3) -> List[str]:
        """
        Compare target text against a list of candidates and return IDs of the top matches.
        """
        if not candidates:
            return []

        target_embedding = self._get_embedding(target_text)
        scores = []

        for cand in candidates:
            cand_embedding = self._get_embedding(cand['description'])
            score = self._cosine_similarity(target_embedding, cand_embedding)
            scores.append((cand['id'], score))

        # Sort by score descending and take top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scores[:top_n] if s[1] > 0.0]

    def detect_duplicates(self, requirements: List[Dict[str, str]], threshold: float = 0.85) -> List[Dict[str, Any]]:
        """
        Compare all requirements against each other to find duplicates.
        
        Args:
            requirements: List of {'id': '...', 'description': '...'}
            threshold: Similarity score above which requirements are considered duplicates.
            
        Returns:
            List of duplicate matches.
        """
        if len(requirements) < 2:
            return []

        # 1. Generate embeddings for all requirements
        embeddings = {}
        for req in requirements:
            embeddings[req['id']] = self._get_embedding(req['description'])

        duplicates = []
        req_ids = [req['id'] for req in requirements]
        
        # 2. Compute similarities (O(n^2) comparison)
        for i in range(len(req_ids)):
            for j in range(i + 1, len(req_ids)):
                id1, id2 = req_ids[i], req_ids[j]
                score = self._cosine_similarity(embeddings[id1], embeddings[id2])
                
                if score > threshold:
                    duplicates.append({
                        'req_id': id2,
                        'similar_to': id1,
                        'score': round(float(score), 4)
                    })
                    
        return duplicates
