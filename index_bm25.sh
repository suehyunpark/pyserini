#!/bin/bash
INPUT=$1
INDEX=$2
NUM_THREADS=$3

shift 3

python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input $INPUT \
  --index $INDEX \
  --generator DefaultLuceneDocumentGenerator \
  --threads $NUM_THREADS \
  --storePositions --storeDocvectors --storeRaw