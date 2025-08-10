#!bin/bash
ALPHA=$1

shift 1

python convert_trec_run_to_dpr_retrieval_run.py \
	--sparse-index indexes/amazon/v2/bm25/ \
	--input-prefix runs/val_sample_annotated_v2/alpha-${ALPHA}/amazon_v2 \

python amazon_retriever_recall.py \
    --results-file /home/miyoung/suehyun/pyserini/runs/val_sample_annotated_v2/alpha-${ALPHA}/amazon_v2_k100.json \
	--k-range "1,3,5,10,20,50,100"