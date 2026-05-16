"""
IBM watsonx.ai client for Granite LLM integration.

Provides async interface to watsonx.ai foundation models including
text generation and embeddings.
"""
from typing import Optional, List, Dict, Any
import asyncio
from functools import partial

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class WatsonxClient:
    """
    Async client for IBM watsonx.ai Granite models.
    
    Provides methods for text generation and embeddings using
    IBM's Granite foundation models.
    """
    
    def __init__(self):
        """Initialize watsonx.ai client with credentials from settings."""
        self.credentials = Credentials(
            url=settings.WATSONX_URL,
            api_key=settings.WATSONX_API_KEY,
        )
        self.project_id = settings.WATSONX_PROJECT_ID
        self.default_model_id = settings.DEFAULT_MODEL_ID
        self.embedding_model_id = settings.EMBEDDING_MODEL_ID
        
        logger.info(f"Initialized watsonx.ai client with model: {self.default_model_id}")
    
    def _get_model(
        self,
        model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> ModelInference:
        """
        Get a model inference instance.
        
        Args:
            model_id: Model ID to use (defaults to configured model)
            params: Generation parameters
            
        Returns:
            ModelInference instance
        """
        model_id = model_id or self.default_model_id
        
        # Default generation parameters
        default_params = {
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 2048,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_P: 0.9,
            GenParams.TOP_K: 50,
            GenParams.REPETITION_PENALTY: 1.1,
        }
        
        # Merge with provided params
        if params:
            default_params.update(params)
        
        return ModelInference(
            model_id=model_id,
            credentials=self.credentials,
            project_id=self.project_id,
            params=default_params,
        )
    
    async def generate(
        self,
        prompt: str,
        model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> str:
        """
        Generate text using Granite model.
        
        Args:
            prompt: Input prompt for generation
            model_id: Model ID to use (optional)
            params: Generation parameters (optional)
            stream: Whether to stream the response (not yet implemented)
            
        Returns:
            Generated text
            
        Example:
            ```python
            client = WatsonxClient()
            response = await client.generate("Explain quantum computing")
            print(response)
            ```
        """
        try:
            model = self._get_model(model_id, params)
            
            # Run synchronous API call in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                partial(model.generate_text, prompt=prompt)
            )
            
            logger.info(f"Generated text for prompt (length: {len(prompt)})")
            return response
            
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise
    
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        model_id: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate text with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model_id: Model ID to use (optional)
            params: Generation parameters (optional)
            
        Returns:
            Generated text
            
        Example:
            ```python
            messages = [
                {"role": "user", "content": "What is Python?"},
                {"role": "assistant", "content": "Python is a programming language."},
                {"role": "user", "content": "What are its main features?"}
            ]
            response = await client.generate_with_history(messages)
            ```
        """
        # Format messages into a single prompt
        prompt = self._format_messages(messages)
        return await self.generate(prompt, model_id, params)
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """
        Format conversation messages into a prompt.
        
        Args:
            messages: List of message dicts
            
        Returns:
            Formatted prompt string
        """
        formatted = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                formatted.append(f"System: {content}")
            elif role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        formatted.append("Assistant:")
        return "\n\n".join(formatted)
    
    async def generate_embeddings(
        self,
        texts: List[str],
        model_id: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for texts.
        
        Args:
            texts: List of texts to embed
            model_id: Embedding model ID (optional)
            
        Returns:
            List of embedding vectors
            
        Example:
            ```python
            texts = ["Hello world", "How are you?"]
            embeddings = await client.generate_embeddings(texts)
            ```
        """
        try:
            model_id = model_id or self.embedding_model_id
            model = ModelInference(
                model_id=model_id,
                credentials=self.credentials,
                project_id=self.project_id,
            )
            
            embeddings = []
            loop = asyncio.get_event_loop()
            
            for text in texts:
                embedding = await loop.run_in_executor(
                    None,
                    partial(model.generate_text_embedding, text=text)
                )
                embeddings.append(embedding)
            
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embeddings = await self.generate_embeddings([text])
        return embeddings[0]


# Global client instance
watsonx_client = WatsonxClient()

# Made with Bob
