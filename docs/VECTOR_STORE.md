# ChromaDB Vector Store Documentation

## Overview

The Credit Risk RAG System uses ChromaDB as its vector database for storing and retrieving document embeddings. This enables semantic search capabilities for finding relevant credit risk information.

## Architecture

### Components

1. **VectorStore Client** (`src/data/vector_store.py`)
   - High-level interface for all vector operations
   - Connection pooling for efficient resource usage
   - Automatic retry logic for resilience
   - Comprehensive error handling

2. **Configuration** (`src/data/config.py`)
   - Centralized settings management
   - Environment-based configuration
   - Sensible defaults for development

3. **Data Models** (`src/data/models.py`)
   - Type-safe document representations
   - Query request/response models
   - Health check models

4. **API Routes** (`src/api/routes.py`)
   - RESTful endpoints for vector operations
   - FastAPI integration
   - Request/response validation

## Configuration

### Environment Variables

```bash
# ChromaDB Connection
CHROMA_HOST=localhost              # ChromaDB server host
CHROMA_PORT=8001                   # ChromaDB server port
CHROMA_URL=http://localhost:8001   # Full URL (overrides host/port)

# Authentication (optional)
CHROMA_AUTH_CREDENTIALS=admin:admin
CHROMA_AUTH_PROVIDER=chromadb.auth.basic.BasicAuthServerProvider

# Collection Settings
CHROMA_COLLECTION_NAME=credit_risk_documents

# Embedding Model
CHROMA_EMBEDDING_FUNCTION=sentence-transformers/all-mpnet-base-v2

# Connection Pool
CHROMA_MAX_CONNECTIONS=10          # Maximum concurrent connections
CHROMA_CONNECTION_TIMEOUT=30       # Connection timeout (seconds)

# Performance
CHROMA_BATCH_SIZE=100              # Default batch size
CHROMA_MAX_RETRIES=3               # Maximum retry attempts
CHROMA_RETRY_DELAY=1.0             # Initial retry delay (seconds)

# Storage (for persistent mode)
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

## Usage Examples

### Python Client

#### Basic Setup

```python
from src.data import VectorStore, Document, QueryRequest

# Initialize vector store (uses environment config)
store = VectorStore()

# Or with custom settings
from src.data import ChromaDBSettings

settings = ChromaDBSettings(
    host="localhost",
    port=8001,
    collection_name="my_collection"
)
store = VectorStore(settings=settings)
```

#### Adding Documents

```python
# Create documents
documents = [
    Document(
        id="doc1",
        content="Credit risk assessment for corporate borrowers",
        metadata={"type": "financial", "year": 2024}
    ),
    Document(
        id="doc2",
        content="Portfolio diversification strategies",
        metadata={"type": "strategy", "year": 2024}
    )
]

# Add to vector store
result = store.add_documents(documents)
print(f"Added {result['added']} documents")

# Batch processing
large_batch = [Document(id=f"doc_{i}", content=f"Content {i}")
               for i in range(1000)]
result = store.add_documents(large_batch, batch_size=100)
```

#### Querying Documents

```python
# Text-based query
query = QueryRequest(
    query_text="credit risk management strategies",
    n_results=5
)
results = store.query(query)

for result in results:
    print(f"ID: {result.id}")
    print(f"Content: {result.content}")
    print(f"Distance: {result.distance}")
    print(f"Metadata: {result.metadata}")
    print("---")

# Query with metadata filter
query = QueryRequest(
    query_text="risk assessment",
    n_results=10,
    where={"type": "financial", "year": 2024}
)
results = store.query(query)

# Query with embedding vector
embedding = [0.1, 0.2, 0.3, ...]  # Pre-computed embedding
query = QueryRequest(
    query_embedding=embedding,
    n_results=5,
    include_embeddings=True  # Include embeddings in results
)
results = store.query(query)
```

#### Updating Documents

```python
# Update existing documents
updated_docs = [
    Document(
        id="doc1",
        content="Updated content for credit risk assessment",
        metadata={"type": "financial", "year": 2024, "updated": True}
    )
]

result = store.update_documents(updated_docs)
print(f"Updated {result['updated']} documents")
```

#### Deleting Documents

```python
# Delete by IDs
result = store.delete_documents(ids=["doc1", "doc2"])

# Delete by metadata filter
result = store.delete_documents(
    where={"year": {"$lt": 2020}}  # Delete documents before 2020
)
```

#### Collection Information

```python
# Get collection stats
info = store.get_collection_info()
print(f"Collection: {info.name}")
print(f"Document count: {info.count}")
print(f"Metadata: {info.metadata}")
```

#### Health Check

```python
# Check vector store health
status = store.health_check()
print(f"Status: {status.status}")
print(f"Latency: {status.latency_ms}ms")
print(f"Details: {status.details}")
```

### REST API

#### Health Endpoints

```bash
# Basic health check
curl http://localhost:8000/health

# ChromaDB-specific health
curl http://localhost:8000/health/chromadb

# Kubernetes readiness probe
curl http://localhost:8000/health/ready

# Kubernetes liveness probe
curl http://localhost:8000/health/live
```

#### Document Operations

```bash
# Add documents
curl -X POST http://localhost:8000/api/v1/vector/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc1",
        "content": "Credit risk assessment",
        "metadata": {"type": "financial"}
      }
    ]
  }'

# Query documents
curl -X POST http://localhost:8000/api/v1/vector/query \
  -H "Content-Type: application/json" \
  -d '{
    "query_text": "credit risk",
    "n_results": 5,
    "where": {"type": "financial"}
  }'

# Update documents
curl -X PUT http://localhost:8000/api/v1/vector/documents \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "id": "doc1",
        "content": "Updated content",
        "metadata": {"type": "financial", "updated": true}
      }
    ]
  }'

# Delete documents
curl -X DELETE "http://localhost:8000/api/v1/vector/documents?ids=doc1&ids=doc2"

# Get collection info
curl http://localhost:8000/api/v1/vector/collections/credit_risk_documents
```

## Performance Characteristics

### Benchmarks

Based on issue requirements:

- **Query Latency**: < 100ms for 10,000 vectors
- **Batch Insert Rate**: > 1,000 embeddings/second
- **Connection Pool**: Supports 10 concurrent connections by default

### Optimization Tips

1. **Batch Operations**: Use batch processing for large datasets
   ```python
   store.add_documents(docs, batch_size=100)
   ```

2. **Connection Pooling**: Reuse the same VectorStore instance
   ```python
   # Good: Reuse instance
   store = VectorStore()
   for batch in batches:
       store.add_documents(batch)

   # Bad: Create new instance each time
   for batch in batches:
       store = VectorStore()  # Creates new connections
       store.add_documents(batch)
   ```

3. **Query Optimization**: Use metadata filters to narrow results
   ```python
   query = QueryRequest(
       query_text="risk",
       n_results=5,
       where={"type": "financial"}  # Filter before semantic search
   )
   ```

4. **Embedding Caching**: Pre-compute embeddings when possible
   ```python
   # Compute embeddings once
   embeddings = embedding_model.encode(texts)

   # Add documents with pre-computed embeddings
   docs = [
       Document(id=str(i), content=text, embedding=emb.tolist())
       for i, (text, emb) in enumerate(zip(texts, embeddings))
   ]
   store.add_documents(docs)
   ```

## Error Handling

### Custom Exceptions

```python
from src.data import (
    VectorDBError,      # Base exception
    ConnectionError,    # Connection failures
    CollectionError,    # Collection operations
    EmbeddingError,     # Embedding generation
    QueryError,         # Query operations
    ValidationError,    # Input validation
)

# Example error handling
try:
    store.add_documents(documents)
except ValidationError as e:
    print(f"Invalid input: {e}")
except EmbeddingError as e:
    print(f"Embedding generation failed: {e}")
except CollectionError as e:
    print(f"ChromaDB operation failed: {e}")
except VectorDBError as e:
    print(f"Vector database error: {e}")
```

### Retry Logic

The client automatically retries failed operations:

- **Max Retries**: 3 (configurable)
- **Retry Delay**: Exponential backoff (1s, 2s, 4s, ...)
- **Retryable Errors**: Connection errors, temporary failures

## Testing

### Unit Tests

```bash
# Run all unit tests
pytest tests/unit/

# Run specific test file
pytest tests/unit/test_vector_store.py

# Run with coverage
pytest tests/unit/ --cov=src/data --cov-report=html
```

### Integration Tests

```bash
# Start ChromaDB first
docker-compose up -d chromadb

# Run integration tests
pytest tests/integration/test_chromadb_integration.py

# Skip integration tests
SKIP_INTEGRATION_TESTS=true pytest

# Or use markers
pytest -m "not integration"
```

## Docker Deployment

### Docker Compose

ChromaDB is pre-configured in `docker-compose.yml`:

```yaml
chromadb:
  image: chromadb/chroma:latest
  container_name: credit-risk-chromadb
  ports:
    - "8001:8000"
  volumes:
    - chroma_data:/chroma/chroma
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### Usage

```bash
# Start all services
docker-compose up -d

# View ChromaDB logs
docker-compose logs -f chromadb

# Check health
curl http://localhost:8001/api/v1/heartbeat

# Stop services
docker-compose down

# Stop and remove data
docker-compose down -v
```

## Monitoring

### Health Metrics

The health check endpoint provides:

```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "latency_ms": 5.2,
  "details": {
    "heartbeat": 1234567890,
    "connection_pool": {
      "max_connections": 10,
      "active_connections": 3
    }
  }
}
```

### Logging

All operations are logged with structured information:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# VectorStore operations will log:
# - Connection attempts
# - Query execution
# - Document additions/updates/deletions
# - Errors and retries
```

## Security Best Practices

1. **Authentication**: Configure credentials in production
   ```bash
   CHROMA_AUTH_CREDENTIALS=secure_username:secure_password
   ```

2. **Network Security**: Use private networks in production
   ```yaml
   # docker-compose.yml
   networks:
     - credit-risk-network  # Private network
   ```

3. **Input Validation**: All inputs are validated automatically
   ```python
   # Pydantic models validate inputs
   doc = Document(id="", content="")  # Raises ValidationError
   ```

4. **No Hardcoded Credentials**: Use environment variables
   ```python
   # Good
   settings = get_chroma_settings()  # Reads from environment

   # Bad
   settings = ChromaDBSettings(auth_credentials="admin:admin")
   ```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```
   Problem: Cannot connect to ChromaDB
   Solution: Ensure ChromaDB is running on correct host:port
   Check: docker-compose ps | grep chromadb
   ```

2. **Slow Queries**
   ```
   Problem: Queries take too long
   Solution:
   - Check collection size
   - Use metadata filters
   - Reduce n_results
   - Optimize embedding model
   ```

3. **Memory Issues**
   ```
   Problem: Out of memory errors
   Solution:
   - Reduce batch_size
   - Process documents in smaller chunks
   - Increase Docker memory limits
   ```

4. **Embedding Errors**
   ```
   Problem: Embedding generation fails
   Solution:
   - Check embedding model is downloaded
   - Verify sentence-transformers installation
   - Try smaller model (all-MiniLM-L6-v2)
   ```

## API Reference

See auto-generated API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Additional Resources

- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vector Database Concepts](https://www.pinecone.io/learn/vector-database/)
