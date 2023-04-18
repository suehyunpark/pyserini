from argparse import ArgumentParser
from pyserini.search.lucene import LuceneSearcher
from pathlib import Path
from glob import glob

import json

DELIMITER = "<DL>"

def format_output(query: dict):
    return {
        "id": query["num"],
        "question": f"title: {query['q_title']}\nbody:{query['q_body']}",
        "answers": query["comments"],
        "ctxs": []
    }
    
def format_ctxs(passage_id, passage, score):
    title, body = passage["contents"].split(DELIMITER)
    return {
        "id": passage_id,
        "title": title,
        "text": body,
        "score": score
    }


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--sparse-index", required=True, help="Path to sparse index to retrieve passages texts from.")
    parser.add_argument("--input-prefix", required=True, help="Input TREC run file.")
    # parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    
    with open('/home/miyoung/suehyun/DPR/input/retriever/reddit/val_sample_annotated_v1.json', 'r', encoding='utf-8') as f:
        queries = json.load(f)
    output = [format_output(query) for query in queries]
    searcher = LuceneSearcher(args.sparse_index)
    
    results_path = Path(args.input_prefix).parent
    prefix = Path(args.input_prefix).stem
    for results_file in results_path.glob(f"{prefix}_k*.trec"):
        k = int(results_file.stem.split("_k")[-1])
        with open(results_file) as f:
            retrieved_all = f.read().splitlines()
        retrieved_per_query = [retrieved_all[i:i+k] for i in range(0, len(retrieved_all), k)]
        for query, retrieved in zip(output, retrieved_per_query):
            for line in retrieved:
                question_id, _, passage_id, rank, score, _ = line.strip().split()
                passage = json.loads(searcher.doc(passage_id).raw())
                query['ctxs'].append(format_ctxs(passage_id, passage, score))
        output_file = Path(str(results_file).replace(".trec", ".json"))
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=4)