"""
Web crawler for extracting content from Docusaurus website.
Extracts clean text from deployed site, filtering out navigation and UI elements.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocusaurusCrawler:
    """Crawler specifically designed for Docusaurus documentation sites."""

    def __init__(self, base_url: str, delay: float = 0.5):
        """
        Initialize the crawler.

        Args:
            base_url: Base URL of the Docusaurus site
            delay: Delay between requests in seconds (be respectful)
        """
        self.base_url = base_url.rstrip('/')
        self.delay = delay
        self.visited_urls = set()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'RAG-Pipeline-Crawler/1.0 (Educational Purpose)'
        })

    def extract_page_content(self, url: str) -> Optional[Dict[str, any]]:
        """
        Extract clean content from a single page.

        Args:
            url: Full URL to extract content from

        Returns:
            Dictionary containing page metadata and content, or None if failed
        """
        if url in self.visited_urls:
            logger.info(f"Skipping already visited: {url}")
            return None

        try:
            logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            self.visited_urls.add(url)
            time.sleep(self.delay)

            soup = BeautifulSoup(response.text, "html.parser")

            # Extract title
            title = self._extract_title(soup)

            # Extract main content (Docusaurus specific selectors)
            content = self._extract_main_content(soup)

            if not content:
                logger.warning(f"No content extracted from: {url}")
                return None

            # Extract metadata
            module = self._extract_module_from_url(url)

            return {
                'url': url,
                'title': title,
                'content': content,
                'module': module,
            }

        except requests.RequestException as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title from HTML."""
        # Try h1 first (usually the main title in Docusaurus)
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        # Fallback to title tag
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()

        return "Untitled"

    def _extract_main_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content from Docusaurus page.
        Filters out navigation, sidebars, footer, etc.
        """
        # Docusaurus main content is typically in article or main tags
        # with specific class names
        content_selectors = [
            'article',
            'main',
            '.markdown',
            '[class*="docMainContainer"]',
            '[class*="docItemContainer"]',
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        if not content_element:
            # Fallback: try to get body content
            content_element = soup.find('body')

        if not content_element:
            return ""

        # Remove unwanted elements
        unwanted_selectors = [
            'nav',
            'header',
            'footer',
            '.navbar',
            '.sidebar',
            '[class*="tableOfContents"]',
            '[class*="breadcrumb"]',
            '.pagination-nav',
            '.theme-edit-this-page',
            '.theme-last-updated',
            'button',
            'script',
            'style',
        ]

        for selector in unwanted_selectors:
            for element in content_element.select(selector):
                element.decompose()

        # Extract text while preserving structure
        text = content_element.get_text(separator='\n', strip=True)

        # Clean up excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]

        return '\n'.join(lines)

    def _extract_module_from_url(self, url: str) -> Optional[str]:
        """Extract module name from URL path."""
        path = urlparse(url).path
        parts = path.strip('/').split('/')

        # Look for module-XX pattern
        for part in parts:
            if part.startswith('module-'):
                return part

        return None

    def crawl_docs_path(self, docs_path: str) -> List[Dict[str, any]]:
        """
        Crawl a documentation path and extract all linked pages.

        Args:
            docs_path: Relative path to documentation (e.g., '/docs/module-01')

        Returns:
            List of extracted page content dictionaries
        """
        start_url = urljoin(self.base_url, docs_path)
        pages = []

        # Extract the starting page
        page_data = self.extract_page_content(start_url)
        if page_data:
            pages.append(page_data)

            # Find and crawl linked pages within the same path
            linked_pages = self._find_linked_pages(start_url, docs_path)
            for linked_url in linked_pages:
                linked_data = self.extract_page_content(linked_url)
                if linked_data:
                    pages.append(linked_data)

        return pages

    def _find_linked_pages(self, current_url: str, base_path: str) -> List[str]:
        """
        Find all documentation pages linked from the current page.
        Only returns URLs under the same base_path.
        """
        try:
            response = self.session.get(current_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']

                # Convert relative URLs to absolute
                absolute_url = urljoin(current_url, href)

                # Parse URL
                parsed = urlparse(absolute_url)

                # Filter: same domain, contains base_path, not already visited
                if (parsed.netloc == urlparse(self.base_url).netloc and
                    base_path in parsed.path and
                    absolute_url not in self.visited_urls and
                    not parsed.fragment):  # Ignore anchor links

                    # Remove query parameters and normalize
                    clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    links.append(clean_url)

            return list(set(links))  # Deduplicate

        except Exception as e:
            logger.error(f"Error finding links from {current_url}: {e}")
            return []

    def crawl_all_docs(self, docs_paths: List[str]) -> List[Dict[str, any]]:
        """
        Crawl multiple documentation paths.

        Args:
            docs_paths: List of relative documentation paths

        Returns:
            List of all extracted page content dictionaries
        """
        all_pages = []

        for path in docs_paths:
            logger.info(f"Crawling documentation path: {path}")
            pages = self.crawl_docs_path(path)
            all_pages.extend(pages)
            logger.info(f"Extracted {len(pages)} pages from {path}")

        logger.info(f"Total pages extracted: {len(all_pages)}")
        return all_pages
