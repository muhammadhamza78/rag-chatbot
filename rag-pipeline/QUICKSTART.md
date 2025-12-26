
cp .env.example .env

# Edit .env with your favorite editor
# Add your API keys and website URL
```

Your `.env` should look like:

```env
COHERE_API_KEY=abc123...
QDRANT_URL=https://xyz.qdrant.io
QDRANT_API_KEY=xyz789...
QDRANT_COLLECTION_NAME=physical_ai_book
WEBSITE_BASE_URL=https://your-site.vercel.app
```

## Step 4: Verify Setup

```bash
python check_setup.py
```

This will verify:
- All packages are installed
- API keys are configured
- Cohere connection works
- Qdrant connection works
- Website is accessible

## Step 5: Run Ingestion

```bash
# First run - create collection
python ingest.py --recreate-collection
```

This will:
1. Crawl your Docusaurus site
2. Extract and chunk content
3. Generate embeddings with Cohere
4. Store in Qdrant

Expected time: 5-10 minutes for ~50 pages

## Step 6: Test Search

```bash
# Run sample queries
python search.py --sample-queries

# Or search with your own query
python search.py "What is physical AI?"
```

You should see relevant results with similarity scores!

## Next Steps

- Integrate search into your application
- Add reranking for better results
- Connect to an LLM for answer generation
- Build a chat interface

## Troubleshooting

**"Module not found" error**:
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**"API key is invalid" error**:
- Double-check your API keys in `.env`
- Ensure no extra spaces or quotes

**"No content extracted" error**:
- Verify `WEBSITE_BASE_URL` is correct
- Make sure site is deployed and public
- Try accessing the URL in your browser

**Need help?**
- Check the full [README.md](README.md)
- Review error messages in console output
- Inspect intermediate JSON files in `output/`
