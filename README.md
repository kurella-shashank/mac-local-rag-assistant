# Mac Local RAG Assistant

A privacy-aware, local-first Retrieval-Augmented Generation (RAG)
assistant for macOS.

## Goals

- Discover authorized local files and folders.
- Extract and process supported documents.
- Search document content using semantic and hybrid retrieval.
- Answer questions with references to original sources.
- Protect private and sensitive information.

## Technology

- Python 3.12
- uv for dependency management
- Docling for document extraction (planned)
- SQLite for metadata (planned)
- Qdrant for vector retrieval (planned)

## Current Status

Phase 0 and Phase 1: Development environment and Git setup.

## Privacy

Local documents, indexes, credentials, and generated data
must not be committed to Git.
EOF
