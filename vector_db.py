"""Vector database integration for storing and retrieving form data.

Uses ChromaDB for semantic search of previously filled forms.
"""
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    import chromadb
    from chromadb.config import Settings
    chroma_available = True
except ImportError:
    chroma_available = False


class VectorDB:
    """Vector database for storing and retrieving form submissions."""

    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize the vector database.

        Args:
            persist_directory: Directory to persist the database
        """
        if not chroma_available:
            raise RuntimeError(
                "chromadb not installed. Run: pip install chromadb")

        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name="form_submissions",
            metadata={"hnsw:space": "cosine"}
        )

    def add_submission(self, form_data: Dict[str, Any], template_name: str, metadata: Optional[Dict] = None):
        """Store a form submission in the vector database.

        Args:
            form_data: The filled form data
            template_name: Name of the template used
            metadata: Additional metadata to store
        """
        submission_id = f"{template_name}_{datetime.now().isoformat()}"

        # Create searchable text from form data
        text_content = " ".join(
            [f"{k}: {v}" for k, v in form_data.items() if v])

        meta = metadata or {}
        meta.update({
            "template": template_name,
            "timestamp": datetime.now().isoformat(),
            "data": json.dumps(form_data)
        })

        self.collection.add(
            documents=[text_content],
            metadatas=[meta],
            ids=[submission_id]
        )

    def search_similar(self, query: str, template_name: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar form submissions.

        Args:
            query: Search query
            template_name: Filter by template name
            top_k: Number of results to return

        Returns:
            List of similar submissions with their data
        """
        where_filter = {"template": template_name} if template_name else None

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )

        submissions = []
        if results and results['metadatas']:
            for metadata in results['metadatas'][0]:
                submissions.append({
                    "data": json.loads(metadata['data']),
                    "template": metadata['template'],
                    "timestamp": metadata['timestamp']
                })

        return submissions

    def get_most_common_values(self, template_name: str, field_name: str, limit: int = 10) -> List[str]:
        """Get most common values for a specific field.

        Args:
            template_name: Template name to filter by
            field_name: Field name to get values for
            limit: Maximum number of results

        Returns:
            List of most common values
        """
        results = self.collection.get(
            where={"template": template_name},
            limit=limit
        )

        values = []
        if results and results['metadatas']:
            for metadata in results['metadatas']:
                data = json.loads(metadata['data'])
                if field_name in data and data[field_name]:
                    values.append(data[field_name])

        # Return unique values
        return list(set(values))

    def get_user_history(self, user_identifier: str, template_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get submission history for a specific user.

        Args:
            user_identifier: User email or name to search for
            template_name: Optional template filter

        Returns:
            List of user's previous submissions
        """
        return self.search_similar(user_identifier, template_name, top_k=10)


def get_autofill_data(query: str, template_name: str, db: Optional[VectorDB] = None) -> Dict[str, Any]:
    """Get autofill data from vector DB based on query.

    Args:
        query: User's input text
        template_name: Template being filled
        db: VectorDB instance (creates new one if None)

    Returns:
        Dictionary of field values to autofill
    """
    if not db:
        try:
            db = VectorDB()
        except RuntimeError:
            return {}

    # Search for similar submissions
    similar = db.search_similar(query, template_name, top_k=1)

    if similar:
        return similar[0]['data']

    return {}
