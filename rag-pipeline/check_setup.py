"""
Setup verification script.
Checks that all configuration is correct before running the pipeline.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def check_imports():
    """Verify all required packages are installed."""
    logger.info("Checking package imports...")
    packages = {
        'requests': 'requests',
        'bs4': 'beautifulsoup4',
        'cohere': 'cohere',
        'qdrant_client': 'qdrant-client',
        'dotenv': 'python-dotenv',
    }

    missing = []
    for module, package in packages.items():
        try:
            __import__(module)
            logger.info(f"  ✓ {package}")
        except ImportError:
            logger.error(f"  ✗ {package} - NOT INSTALLED")
            missing.append(package)

    return len(missing) == 0, missing


def check_config():
    """Verify configuration is set correctly."""
    logger.info("\nChecking configuration...")

    try:
        import config

        checks = {
            'COHERE_API_KEY': config.COHERE_API_KEY,
            'QDRANT_URL': config.QDRANT_URL,
            'QDRANT_API_KEY': config.QDRANT_API_KEY,
            'WEBSITE_BASE_URL': config.WEBSITE_BASE_URL,
        }

        all_valid = True
        for key, value in checks.items():
            if value and value != f"your_{key.lower()}_here":
                logger.info(f"  ✓ {key} is set")
            else:
                logger.error(f"  ✗ {key} is NOT set or using example value")
                all_valid = False

        return all_valid

    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return False


def check_cohere_connection():
    """Test Cohere API connection."""
    logger.info("\nTesting Cohere API connection...")

    try:
        import config
        import cohere

        client = cohere.Client(config.COHERE_API_KEY)

        # Test with a simple embedding
        response = client.embed(
            texts=["test"],
            model=config.EMBEDDING_MODEL,
            input_type=config.EMBEDDING_INPUT_TYPE
        )

        logger.info(f"  ✓ Cohere API connected successfully")
        logger.info(f"  ✓ Using model: {config.EMBEDDING_MODEL}")
        logger.info(f"  ✓ Embedding dimension: {len(response.embeddings[0])}")
        return True

    except Exception as e:
        logger.error(f"  ✗ Cohere API error: {e}")
        return False


def check_qdrant_connection():
    """Test Qdrant connection."""
    logger.info("\nTesting Qdrant connection...")

    try:
        import config
        from qdrant_client import QdrantClient

        client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)

        # List collections
        collections = client.get_collections()

        logger.info(f"  ✓ Qdrant connected successfully")
        logger.info(f"  ✓ Existing collections: {len(collections.collections)}")

        return True

    except Exception as e:
        logger.error(f"  ✗ Qdrant connection error: {e}")
        return False


def check_website_access():
    """Test if website is accessible."""
    logger.info("\nTesting website access...")

    try:
        import config
        import requests

        response = requests.get(config.WEBSITE_BASE_URL, timeout=10)
        response.raise_for_status()

        logger.info(f"  ✓ Website is accessible")
        logger.info(f"  ✓ URL: {config.WEBSITE_BASE_URL}")
        logger.info(f"  ✓ Status: {response.status_code}")
        return True

    except Exception as e:
        logger.error(f"  ✗ Website access error: {e}")
        logger.error(f"  ✗ URL: {config.WEBSITE_BASE_URL}")
        return False


def main():
    """Run all checks."""
    print("=" * 80)
    print("RAG PIPELINE SETUP VERIFICATION")
    print("=" * 80)

    results = {}

    # Check imports
    imports_ok, missing = check_imports()
    results['imports'] = imports_ok

    if not imports_ok:
        logger.error(f"\nMissing packages: {', '.join(missing)}")
        logger.error("Install them with: pip install -r requirements.txt")
        return False

    # Check config
    results['config'] = check_config()

    if not results['config']:
        logger.error("\nPlease configure your .env file with valid credentials")
        return False

    # Check connections
    results['cohere'] = check_cohere_connection()
    results['qdrant'] = check_qdrant_connection()
    results['website'] = check_website_access()

    # Summary
    print("\n" + "=" * 80)
    print("SETUP VERIFICATION SUMMARY")
    print("=" * 80)

    all_passed = all(results.values())

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{check.upper():15} {status}")

    print("=" * 80)

    if all_passed:
        logger.info("\n✓ All checks passed! You're ready to run the pipeline.")
        logger.info("\nNext steps:")
        logger.info("  1. Run ingestion: python ingest.py --recreate-collection")
        logger.info("  2. Test search: python search.py --sample-queries")
        return True
    else:
        logger.error("\n✗ Some checks failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
