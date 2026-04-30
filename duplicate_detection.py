import json
import urllib.request
import math

class DuplicateDetector:
    def __init__(self, ollama_url="http://localhost:11434", threshold=0.85):
        """
        Initialize the DuplicateDetector.
        :param ollama_url: Base URL for Ollama API
        :param threshold: Cosine similarity threshold for considering something a duplicate
        """
        self.ollama_url = ollama_url
        self.threshold = threshold
        # In a real app, this might be a vector database like ChromaDB or Qdrant.
        # For this implementation, we use an in-memory store.
        self.vectors = [] 
        
    def _get_embedding(self, text):
        """
        Step 1: Generate embeddings using nomic-embed-text via Ollama.
        """
        url = f"{self.ollama_url}/api/embeddings"
        data = {
            "model": "nomic-embed-text",
            "prompt": text
        }
        
        req = urllib.request.Request(url, data=json.dumps(data).encode("utf-8"), headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode("utf-8"))
                return result.get("embedding", [])
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return []

    def _cosine_similarity(self, vec1, vec2):
        """
        Calculate cosine similarity between two vectors.
        """
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
            
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
            
        return dot_product / (magnitude1 * magnitude2)

    def store_requirement(self, req_id, text):
        """
        Step 2: Generate embedding and store the vector with its ID and original text.
        """
        embedding = self._get_embedding(text)
        if embedding:
            self.vectors.append({
                "id": req_id,
                "text": text,
                "embedding": embedding
            })
            return True
        return False

    def find_duplicates(self, new_text):
        """
        Step 3 & 4: Compare new requirement and return similar ones above the threshold.
        """
        new_embedding = self._get_embedding(new_text)
        if not new_embedding:
            return []
            
        similar_reqs = []
        for stored in self.vectors:
            similarity = self._cosine_similarity(new_embedding, stored["embedding"])
            if similarity >= self.threshold:
                similar_reqs.append({
                    "id": stored["id"],
                    "text": stored["text"],
                    "similarity": round(similarity, 4)
                })
                
        # Sort by similarity in descending order
        similar_reqs.sort(key=lambda x: x["similarity"], reverse=True)
        return similar_reqs

# Example Usage
if __name__ == "__main__":
    detector = DuplicateDetector(threshold=0.80)
    
    print("Storing existing requirements...")
    detector.store_requirement("REQ-001", "The system shall allow users to log in using their email and password.")
    detector.store_requirement("REQ-002", "The system shall generate a PDF report of monthly sales.")
    detector.store_requirement("REQ-003", "The application must load in under 2 seconds on a 4G connection.")
    
    print("\nChecking a new requirement for duplicates...")
    new_req = "Users must be able to sign in with an email address and a password."
    print(f"New Requirement: '{new_req}'")
    
    duplicates = detector.find_duplicates(new_req)
    
    if duplicates:
        print("\nPotential duplicates found!")
        for dup in duplicates:
            print(f"- {dup['id']} (Similarity: {dup['similarity']}): {dup['text']}")
    else:
        print("\nNo duplicates found.")
