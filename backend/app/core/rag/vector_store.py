"""
Vector store implementation using ChromaDB and pgvector.

Provides document storage, retrieval, and semantic search capabilities.
"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.llm.watsonx_client import watsonx_client
from app.utils.logger import get_logger

logger = get_logger(__name__)


class VectorStore:
    """
    Vector store for document storage and retrieval.
    
    Uses ChromaDB for vector storage and semantic search.
    Integrates with watsonx.ai for generating embeddings.
    """
    
    def __init__(self):
        """Initialize vector store with ChromaDB."""
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.Collection] = None
        self.collection_name = "task_documents"
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    async def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            # Create ChromaDB client
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=settings.CHROMA_PERSIST_DIRECTORY
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Task documents and knowledge base"}
            )
            
            logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise
    
    async def add_document(
        self,
        document: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a document to the vector store.
        
        Args:
            document: Document text to add
            metadata: Optional metadata for the document
            doc_id: Optional document ID (generated if not provided)
            
        Returns:
            Document ID
        """
        if not self.collection:
            await self.initialize()
        
        try:
            # Split document into chunks
            chunks = self.text_splitter.split_text(document)
            
            # Generate embeddings for chunks
            embeddings = await watsonx_client.generate_embeddings(chunks)
            
            # Prepare IDs and metadata
            chunk_ids = [f"{doc_id}_chunk_{i}" if doc_id else f"doc_chunk_{i}" 
                        for i in range(len(chunks))]
            
            chunk_metadata = [
                {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "doc_id": doc_id
                }
                for i in range(len(chunks))
            ]
            
            # Add to ChromaDB
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=chunk_metadata,
                ids=chunk_ids
            )
            
            logger.info(f"Added document with {len(chunks)} chunks to vector store")
            
            return doc_id or chunk_ids[0]
            
        except Exception as e:
            logger.error(f"Error adding document to vector store: {e}")
            raise
    
    async def search(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using semantic search.
        
        Args:
            query: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of search results with documents and metadata
        """
        if not self.collection:
            await self.initialize()
        
        try:
            # Generate query embedding
            query_embedding = await watsonx_client.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata
            )
            
            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    "id": results['ids'][0][i],
                    "document": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i] if 'distances' in results else None
                })
            
            logger.info(f"Search returned {len(formatted_results)} results for query: {query[:50]}...")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {e}")
            raise
    
    async def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        if not self.collection:
            await self.initialize()
        
        try:
            # Delete all chunks for this document
            self.collection.delete(
                where={"doc_id": doc_id}
            )
            
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store collection.
        
        Returns:
            Collection statistics
        """
        if not self.collection:
            await self.initialize()
        
        try:
            count = self.collection.count()
            
            return {
                "collection_name": self.collection_name,
                "document_count": count,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collection_name": self.collection_name,
                "error": str(e),
                "status": "error"
            }


# Global vector store instance
vector_store = VectorStore()

# Made with Bob
