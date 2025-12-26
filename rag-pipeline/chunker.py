"""
Text chunking module for splitting documents into semantically meaningful chunks.
Uses heading-based and size-based chunking with overlap for context preservation.
"""

import re
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextChunker:
    """Intelligent text chunker that respects document structure."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        """
        Initialize the chunker.

        Args:
            chunk_size: Target size for chunks in words
            chunk_overlap: Number of words to overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, document: Dict[str, any]) -> List[Dict[str, any]]:
        """
        Chunk a document into smaller pieces with metadata.

        Args:
            document: Document dictionary with 'content', 'url', 'title', 'module'

        Returns:
            List of chunk dictionaries with text and metadata
        """
        content = document['content']
        url = document['url']
        title = document['title']
        module = document.get('module')

        # Split content into sections based on headings
        sections = self._split_by_headings(content)

        # Process each section into chunks
        chunks = []
        for section in sections:
            section_chunks = self._chunk_section(
                section['text'],
                section['headings'],
                url,
                title,
                module
            )
            chunks.extend(section_chunks)

        # Add chunk indices
        for idx, chunk in enumerate(chunks):
            chunk['chunk_index'] = idx
            chunk['total_chunks'] = len(chunks)
            # Generate unique chunk ID
            chunk['chunk_id'] = f"{self._url_to_id(url)}_{idx}"

        logger.info(f"Created {len(chunks)} chunks from {url}")
        return chunks

    def _split_by_headings(self, text: str) -> List[Dict[str, any]]:
        """
        Split text into sections based on markdown-style headings.

        Args:
            text: Raw text content

        Returns:
            List of sections with heading hierarchy and text
        """
        lines = text.split('\n')
        sections = []
        current_section = {
            'headings': [],
            'text': []
        }
        heading_stack = []

        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')

        for line in lines:
            heading_match = heading_pattern.match(line)

            if heading_match:
                # Save previous section if it has content
                if current_section['text']:
                    current_section['text'] = '\n'.join(current_section['text'])
                    sections.append(current_section)

                # Parse heading
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2).strip()

                # Update heading stack
                # Remove deeper headings
                heading_stack = [h for h in heading_stack if h['level'] < level]
                # Add current heading
                heading_stack.append({'level': level, 'text': heading_text})

                # Start new section
                current_section = {
                    'headings': [h['text'] for h in heading_stack],
                    'text': [line]  # Include heading in text
                }
            else:
                current_section['text'].append(line)

        # Add final section
        if current_section['text']:
            current_section['text'] = '\n'.join(current_section['text'])
            sections.append(current_section)

        return sections

    def _chunk_section(
        self,
        text: str,
        headings: List[str],
        url: str,
        title: str,
        module: str
    ) -> List[Dict[str, any]]:
        """
        Chunk a section into smaller pieces with overlap.

        Args:
            text: Section text
            headings: Hierarchical list of headings for this section
            url: Source URL
            title: Document title
            module: Module name

        Returns:
            List of chunk dictionaries
        """
        words = text.split()

        # If section is smaller than chunk size, return as single chunk
        if len(words) <= self.chunk_size:
            return [{
                'text': text,
                'url': url,
                'title': title,
                'module': module,
                'heading_hierarchy': ' > '.join(headings) if headings else title,
            }]

        # Split into overlapping chunks
        chunks = []
        start = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)

            chunks.append({
                'text': chunk_text,
                'url': url,
                'title': title,
                'module': module,
                'heading_hierarchy': ' > '.join(headings) if headings else title,
            })

            # Move start position with overlap
            start += self.chunk_size - self.chunk_overlap

            # Prevent infinite loop
            if start >= len(words):
                break

        return chunks

    def _url_to_id(self, url: str) -> str:
        """Convert URL to a safe ID string."""
        # Remove protocol and domain, keep path
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
        return url_hash

    def chunk_all_documents(self, documents: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Chunk multiple documents.

        Args:
            documents: List of document dictionaries

        Returns:
            List of all chunks from all documents
        """
        all_chunks = []

        for document in documents:
            chunks = self.chunk_document(document)
            all_chunks.extend(chunks)

        logger.info(f"Total chunks created: {len(all_chunks)}")
        return all_chunks
