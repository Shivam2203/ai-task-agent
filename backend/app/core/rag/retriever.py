"""
RAG retriever for context-aware information retrieval.

Combines vector search with context formatting for agent use.
"""
from typing import List, Dict, Any, Optional

from app.core.rag.vector_store import vector_store
from app.utils.logger import get_logger

logger = get_logger(__name__)


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever.
    
    Provides context retrieval for the agent by searching the vector store
    and formatting results for LLM consumption.
    """
    
    def __init__(self):
        """Initialize RAG retriever."""
        self.vector_store = vector_store
        logger.info("RAGRetriever initialized")
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Retrieve relevant context for a query.
        
        Args:
            query: Search query
            top_k: Number of results to retrieve
            filter_metadata: Optional metadata filters
            
        Returns:
            Formatted context string
        """
        try:
            # Search vector store
            results = await self.vector_store.search(
                query=query,
                n_results=top_k,
                filter_metadata=filter_metadata
            )
            
            # Format context
            context = self._format_context(results)
            
            logger.info(f"Retrieved context for query: {query[:50]}...")
            
            return context
            
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return ""
    
    def _format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format search results into context string.
        
        Args:
            results: List of search results
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant context found."
        
        context_parts = ["Relevant Context:\n"]
        
        for i, result in enumerate(results, 1):
            document = result.get("document", "")
            metadata = result.get("metadata", {})
            
            context_parts.append(f"\n[Context {i}]")
            
            # Add metadata if available
            if metadata:
                if "doc_id" in metadata:
                    context_parts.append(f"Source: {metadata['doc_id']}")
                if "chunk_index" in metadata:
                    context_parts.append(f"Chunk: {metadata['chunk_index'] + 1}/{metadata.get('total_chunks', '?')}")
            
            context_parts.append(f"\n{document}\n")
        
        return "\n".join(context_parts)
    
    async def add_task_context(
        self,
        task_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add task-related context to the vector store.
        
        Args:
            task_id: Task identifier
            content: Content to add
            metadata: Optional metadata
            
        Returns:
            True if successful
        """
        try:
            task_metadata = {
                "task_id": task_id,
                "type": "task_context",
                **(metadata or {})
            }
            
            await self.vector_store.add_document(
                document=content,
                metadata=task_metadata,
                doc_id=f"task_{task_id}"
            )
            
            logger.info(f"Added context for task: {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding task context: {e}")
            return False
    
    async def retrieve_task_history(
        self,
        task_id: str,
        top_k: int = 3
    ) -> str:
        """
        Retrieve historical context for a specific task.
        
        Args:
            task_id: Task identifier
            top_k: Number of results
            
        Returns:
            Formatted task history
        """
        try:
            results = await self.vector_store.search(
                query=f"task {task_id}",
                n_results=top_k,
                filter_metadata={"task_id": task_id}
            )
            
            return self._format_context(results)
            
        except Exception as e:
            logger.error(f"Error retrieving task history: {e}")
            return ""


# Global retriever instance
rag_retriever = RAGRetriever()

# Made with Bob
