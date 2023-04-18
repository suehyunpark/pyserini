#!bin/bash
ALPHA=$1

shift 1

python convert_trec_run_to_dpr_retrieval_run.py \
	--sparse-index indexes/amazon/v1/bm25/ \
	--input-prefix runs/val_sample_annotated_v1/alpha-${ALPHA}/amazon_v1 \

cd ../DPR
python amazon_retriever_recall.py \
    --results-file /home/miyoung/suehyun/pyserini/runs/val_sample_annotated_v1/alpha-${ALPHA}/amazon_v1_k1000.json \
	--k-range "1,3,5,10,20"