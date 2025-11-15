# API Documentation

## Overview

The Credit Risk RAG System provides a RESTful API for credit risk assessment and analysis.

## Base URL

```
Development: http://localhost:8000
Production: https://api.your-domain.com
```

## Authentication

API uses JWT-based authentication:

```bash
# Get access token
POST /api/v1/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# Use token in requests
Authorization: Bearer <token>
```

## Endpoints

### Health Check

```
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### Credit Risk Assessment

```
POST /api/v1/risk/assess
```

Request:
```json
{
  "applicant_id": "12345",
  "data": {
    "income": 50000,
    "employment_years": 5,
    "credit_history": "good"
  },
  "documents": ["base64_encoded_doc"]
}
```

Response:
```json
{
  "risk_score": 0.25,
  "risk_level": "low",
  "explanation": "Applicant shows strong financial history...",
  "factors": {
    "positive": ["Stable income", "Good credit history"],
    "negative": []
  },
  "recommendation": "APPROVE"
}
```

### Document Analysis

```
POST /api/v1/documents/analyze
```

Request:
```json
{
  "document": "base64_encoded_pdf",
  "document_type": "financial_statement"
}
```

### Query Knowledge Base

```
POST /api/v1/rag/query
```

Request:
```json
{
  "query": "What are the requirements for mortgage approval?",
  "top_k": 5
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid input data",
  "errors": [...]
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per organization

## Interactive Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
