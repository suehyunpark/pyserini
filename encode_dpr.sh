# !/bin/bash
INPUT=$1
OUTPUT_PREFIX=$2
NUM_SHARDS=$3
SHARD_ID=$4
DEVICE=$5

shift 5

python -m pyserini.encode \
    input   --corpus $INPUT \
            --fields title text \
            --delimiter "<DL>" \
            --shard-id $SHARD_ID \
            --shard-num $NUM_SHARDS \
    output  --embeddings ${OUTPUT_PREFIX}${SHARD_ID} \
            --to-faiss \
    encoder --encoder facebook/dpr-ctx_encoder-multiset-base \
            --fields title content \
            --batch 64 \
            --device cuda:${DEVICE}