#!bin/bash
DENSE_INDEX=$1
SPARSE_INDEX=$2
ALPHA=$3
OUTPUT_PREFIX=$4
INITIAL_HITS=$5

shift 5

python -m pyserini.search.hybrid \
    dense   --index $DENSE_INDEX \
            --encoder facebook/dpr-question_encoder-multiset-base \
    sparse  --index $SPARSE_INDEX \
    fusion  --alpha $ALPHA \
    run     --topics input/retriever/reddit/val_sample_annotated_v1_pyserini.json \
            --output runs/val_sample_annotated_v1/alpha-${ALPHA}/${OUTPUT_PREFIX}_k${INITIAL_HITS}.trec \
            --hits $INITIAL_HITS
        #     --normalization \