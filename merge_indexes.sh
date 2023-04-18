#!/bin/bash
PREFIX=$1
NUM_SHARDS=$2

shift 2

python -m pyserini.index.merge_faiss_indexes \
    --prefix $PREFIX \
    --shard-num $NUM_SHARDS

echo "Removing partial indexes..."
for i in $(seq 0 $(($NUM_SHARDS - 1))); do
    rm -r ${PREFIX}${i}
done