# Agent Transcript 02 — Debugging pgvector Indexing

## Problem statement

During implementation, vector retrieval depends on several components agreeing:

```text
Embedding model
      ↓
Vector dimensionality
      ↓
PostgreSQL VECTOR column
      ↓
pgvector operator
      ↓
HNSW index
      ↓
Similarity query
```

A mismatch anywhere in this chain can make indexing fail or produce unusable retrieval.

## Debugging checklist

### 1. Confirm the extension

Run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Verify:

```sql
SELECT extname, extversion
FROM pg_extension
WHERE extname = 'vector';
```

Expected result: the `vector` extension is installed.

### 2. Confirm vector dimensionality

The embedding model determines the number of dimensions.

The database column must match that dimension.

Example conceptual schema:

```sql
embedding VECTOR(<embedding_dimension>)
```

Do not guess the dimension. Determine it from the selected embedding model.

### 3. Validate stored vectors

Before creating an index, confirm that vectors exist:

```sql
SELECT COUNT(*) FROM transcript_chunks
WHERE embedding IS NOT NULL;
```

Inspect one vector if needed:

```sql
SELECT id, vector_dims(embedding)
FROM transcript_chunks
WHERE embedding IS NOT NULL
LIMIT 5;
```

Every row used by the index should have the expected dimensionality.

## HNSW indexing

A cosine-distance HNSW index can be created conceptually as:

```sql
CREATE INDEX transcript_chunks_embedding_hnsw
ON transcript_chunks
USING hnsw (embedding vector_cosine_ops);
```

The exact index creation strategy should be validated against the installed pgvector version.

## Query debugging

The retrieval expression:

```sql
1 - (embedding <=> query_vector)
```

converts cosine distance into a similarity-style score.

A debugging query should initially return a small sample:

```sql
SELECT
    id,
    episode_title,
    guest_name,
    1 - (embedding <=> :query_vector) AS similarity
FROM transcript_chunks
WHERE embedding IS NOT NULL
ORDER BY embedding <=> :query_vector
LIMIT 5;
```

## Common failure modes

### Failure: extension not installed

Symptom:

```text
type "vector" does not exist
```

Resolution:

```sql
CREATE EXTENSION vector;
```

If the Docker image does not contain pgvector, use a pgvector-enabled PostgreSQL image.

### Failure: wrong dimensions

Symptom:

```text
different vector dimensions
```

Resolution:

- Check embedding model output dimension.
- Check database column dimension.
- Recreate/migrate incompatible vectors.

### Failure: index exists but retrieval is poor

Possible causes:

- Chunk size too large.
- Chunk size too small.
- Poor transcript parsing.
- Wrong embedding model.
- Similarity threshold too high.
- Missing metadata.
- Query language differs significantly from transcript language.

Resolution:

Evaluate retrieval quality with a small test set before changing multiple variables.

### Failure: SQL parameter casting

When passing a vector through SQLAlchemy, the database must receive a valid vector representation.

Conceptually:

```sql
:vector::vector
```

The application should validate that the generated value is serializable and compatible with the pgvector type.

## Recommended debugging sequence

```text
1. Extension
   ↓
2. Column type
   ↓
3. Embedding dimension
   ↓
4. Stored vector count
   ↓
5. Raw similarity query
   ↓
6. HNSW index
   ↓
7. Application retriever
   ↓
8. End-to-end RAG test
```

This sequence avoids debugging the application layer before confirming that the database can perform a correct raw vector search.

## Retrieval acceptance test

Create a small set of known questions with expected relevant episodes.

For each query verify:

- At least one expected chunk is retrieved.
- Similarity scores are sensible.
- Source metadata is complete.
- Threshold behavior is predictable.
- Top-K ordering is correct.

## Final lesson

The vector index is not the retrieval system by itself. Retrieval quality is the combined result of:

```text
Parsing
+ Chunking
+ Embeddings
+ Database storage
+ Index
+ Query formulation
+ Threshold
+ Metadata
```

Therefore, pgvector debugging should always be performed end-to-end rather than treating the index as an isolated component.
