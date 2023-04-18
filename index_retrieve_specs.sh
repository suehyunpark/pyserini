#!/bin/bash

python -m pyserini.index.lucene \
  --collection "JsonCollection" \
  --input "/home/miyoung/suehyun/amazon/passages/specs" \
  --index "indexes/amazon_specs_passages" \
  --generator "DefaultLuceneDocumentGenerator" \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw

python -m pyserini.search.lucene \
  --index "indexes/amazon_specs_passages" \
  --topics "data/val_samples.tsv" \
  --output "runs/val_samples/bm25.specs.trec" \
  --hits 50 \
  --bm25

python convert_trec_run_to_dpr_retrieval_run.py \
  --index "indexes/amazon_specs_passages" \
  --topics-json "data/val_v3_sample.json" \
  --input "runs/val_samples/bm25.specs.trec" \
  --output "runs/val_samples/bm25.specs.json"