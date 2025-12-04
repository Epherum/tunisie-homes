import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class EmbeddingGenerator:
    """
    Generate embeddings for property descriptions using AI models.
    Supports multiple providers: Google Gemini, OpenAI
    """

    def __init__(self, provider: str = "gemini"):
        """
        Initialize embedding generator.

        Args:
            provider: "gemini" or "openai"
        """
        self.provider = provider.lower()

        if self.provider == "gemini":
            self._init_gemini()
        elif self.provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def _init_gemini(self):
        """Initialize Google Gemini embedding client."""
        try:
            import google.generativeai as genai

            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                print("Warning: GEMINI_API_KEY not found in environment")
                self.client = None
                return

            genai.configure(api_key=api_key)
            self.client = genai
            print("Gemini embedding generator initialized")

        except ImportError:
            print("google-generativeai not installed. Run: pip install google-generativeai")
            self.client = None

    def _init_openai(self):
        """Initialize OpenAI embedding client."""
        try:
            from openai import OpenAI

            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Warning: OPENAI_API_KEY not found in environment")
                self.client = None
                return

            self.client = OpenAI(api_key=api_key)
            print("OpenAI embedding generator initialized")

        except ImportError:
            print("openai not installed. Run: pip install openai")
            self.client = None

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed (property description)

        Returns:
            List of floats representing the embedding vector, or None if failed
        """
        if not self.client:
            print("Embedding client not initialized. Skipping embedding generation.")
            return None

        if not text or not text.strip():
            return None

        try:
            if self.provider == "gemini":
                return self._generate_gemini_embedding(text)
            elif self.provider == "openai":
                return self._generate_openai_embedding(text)
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None

    def _generate_gemini_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding using Google Gemini.
        Uses the embedding-001 model which produces 768-dimensional vectors.
        """
        try:
            result = self.client.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document"
            )

            embedding = result['embedding']
            return embedding

        except Exception as e:
            print(f"Gemini embedding error: {e}")
            return None

    def _generate_openai_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding using OpenAI.
        Uses text-embedding-3-small which produces 1536-dimensional vectors by default.
        """
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text,
                dimensions=768  # Match Gemini's dimension for consistency
            )

            embedding = response.data[0].embedding
            return embedding

        except Exception as e:
            print(f"OpenAI embedding error: {e}")
            return None

    def generate_property_embedding(self, property_data: dict) -> Optional[List[float]]:
        """
        Generate embedding for a property by combining relevant fields.

        Args:
            property_data: Property dictionary with title, description, etc.

        Returns:
            Embedding vector
        """
        # Combine title and description for richer embedding
        text_parts = []

        if property_data.get('title'):
            text_parts.append(property_data['title'])

        if property_data.get('description'):
            text_parts.append(property_data['description'])

        # Add location context
        if property_data.get('city'):
            text_parts.append(f"Ville: {property_data['city']}")

        if property_data.get('region'):
            text_parts.append(f"Région: {property_data['region']}")

        # Add property type if available
        if property_data.get('type'):
            text_parts.append(f"Type: {property_data['type']}")

        combined_text = " ".join(text_parts)

        return self.generate_embedding(combined_text)


# Placeholder/Mock embedding generator for testing without API keys
class MockEmbeddingGenerator:
    """
    Mock embedding generator for testing without API keys.
    Returns dummy embeddings.
    """

    def __init__(self):
        print("Mock embedding generator initialized (no actual embeddings)")

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """Return None (no actual embeddings)."""
        return None

    def generate_property_embedding(self, property_data: dict) -> Optional[List[float]]:
        """Return None (no actual embeddings)."""
        return None
