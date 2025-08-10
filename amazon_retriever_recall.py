import json
from typing import Dict, List
import pandas as pd
from argparse import ArgumentParser
from pathlib import Path


GROUND_TRUTH_FILE = '/home/miyoung/suehyun/reddit/val_sample_annotated_v2.json'


def get_ground_truths(all_ground_truth: List[dict]):
    num_specs_truth = 0
    num_reviews_truth = 0
    ground_truth_ids_dict = {}
    ground_truth_dict = {}
    for annotated in all_ground_truth:
        ground_truth_ids = set()
        if "specs" in annotated:
            specs_ids = [specs["id"] for specs in annotated["specs"]]
            ground_truth_ids.update(specs_ids)
            num_specs_truth += len(specs_ids)
        if "reviews" in annotated:
            review_ids = [review["id"] for review in annotated["reviews"]]
            ground_truth_ids.update(review_ids)
            num_reviews_truth += len(review_ids)
        if ground_truth_ids:
            ground_truth_ids_dict[annotated["num"]] = ground_truth_ids
            ground_truth_dict[annotated["num"]] = annotated
            
    return ground_truth_dict, ground_truth_ids_dict, num_specs_truth, num_reviews_truth
        

def calculate_recall_k(ground_truth_dict: Dict[int, dict], ground_truth_ids_dict: Dict[int, set], retrieved_results: List[dict], k: int):
    filtered_results = [result for result in retrieved_results if result["id"] in ground_truth_ids_dict]
    
    specs_hits = 0
    reviews_hits = 0
    reviews_product_hits = 0
    annotated_results = []
    max_recall_per_query = 0
    for result in filtered_results:
        ground_truth_annotation = ground_truth_dict[result["id"]]
        ground_truth_annotation.pop("specs", None)
        ground_truth_annotation.pop("reviews", None)
        ground_truth_annotation["ctxs"] = []
        
        ground_truth_ids = ground_truth_ids_dict[result["id"]]
        # print(f"Query {result['id']}: {ground_truth_ids}")
        ctx_id_prefix_dict = {ctx["id"].split("_")[0]: (ctx["id"], idx) for idx, ctx in enumerate(result["ctxs"][:k])}  # look at only k retrieved ctxs
        partial_hits = 0
        for ground_truth_id in ground_truth_ids:
            retrieved = False
            exact_match = False
            if "specs" in ground_truth_id:
                ctx_meta = ctx_id_prefix_dict.get(ground_truth_id, None)
                if ctx_meta:
                    retrieved = True
                    exact_match = True
                    specs_hits += 1
                    partial_hits += 1
                # print(f"\tFound:\t{ground_truth_id}")
            else:
                ground_truth_id_prefix = ground_truth_id.split("_")[0]
                ctx_meta = ctx_id_prefix_dict.get(ground_truth_id_prefix, None)
                if ctx_meta:
                    retrieved = True
                    if ctx_meta[0].startswith(ground_truth_id):  # 13- or 14- digit
                        exact_match = True
                        reviews_hits += 1  # exact match
                    reviews_product_hits += 1
                    partial_hits += 1
                    # print(f"\tFound:\t{ground_truth_id}")
            if retrieved:
                ctx = result["ctxs"][ctx_meta[1]]
                # ctx["retrieved"] = retrieved  # True
                ctx["rank"] = ctx_meta[1] + 1
                ctx["exact_match"] = exact_match
                ground_truth_annotation["ctxs"].append(ctx)
                
        annotated_results.append(ground_truth_annotation)
        recall_per_query = partial_hits / len(ground_truth_ids)
        if recall_per_query > max_recall_per_query:
            max_recall_per_query = recall_per_query
                        
    return specs_hits, reviews_hits, reviews_product_hits, max_recall_per_query, annotated_results
    
                
if __name__ == "__main__":
    print("hi")
    parser = ArgumentParser()
    parser.add_argument("--results-file", type=str, required=True, help="Path to the retrieved results file")
    parser.add_argument("--k-range", type=str, help="Range of k values to calculate recall for, comma separated")
    parser.add_argument("--output-success-file-suffix", type=str, default="success")
    args = parser.parse_args()
    with open(GROUND_TRUTH_FILE, 'r') as f:
        all_ground_truth = json.load(f)
    
    ground_truth_dict, ground_truth_ids_dict, num_specs_truth, num_reviews_truth = get_ground_truths(all_ground_truth)
    num_queries = len(ground_truth_ids_dict)
    print("Number of queries in ground truth: {}".format(num_queries))
    print("Number of specs in ground truth: {}".format(num_specs_truth))
    print("Number of reviews in ground truth: {}".format(num_reviews_truth))
    
    recalls = []
    precisions = []
    
    with open(args.results_file, 'r') as f:
        retrieved_results = json.load(f)
    k_range = [int(k) for k in args.k_range.split(",")]
    for k in k_range:
        # results_file = f"{args.results_file_prefix}_k{k}.json"
        specs_hits, reviews_hits, reviews_product_hits, max_recall_per_query, annotated_results = calculate_recall_k(ground_truth_dict, ground_truth_ids_dict, retrieved_results, k)
        recalls.append((k, 
                        f"{specs_hits}({specs_hits/num_specs_truth:.2f})", 
                        f"{reviews_hits}({reviews_hits/num_reviews_truth:.2f})",
                        f"{reviews_product_hits}({reviews_product_hits/num_reviews_truth:.2f})",
                        f"{max_recall_per_query:.2f}",
                        ))
        precisions.append((k,
                           f"{specs_hits}({specs_hits/(k * num_queries):.2f})",
                           f"{reviews_hits}({reviews_hits/(k * num_queries):.2f})",
                           f"{reviews_product_hits}({reviews_product_hits/(k * num_queries):.2f})"
                           ))
        output_file = args.results_file.replace(".json", f"_{args.output_success_file_suffix}_k{k}.json")
        with open(output_file, 'w') as f:
            json.dump(annotated_results, f, indent=2)
        
        
    recalls_df = pd.DataFrame(recalls, columns=['k', 'Recall@k for specs', 'Recall@k for reviews', 'Recall@k for reviews (product level)', 'Max Recall@k per query'])
    precisions_df = pd.DataFrame(precisions, columns=['k', 'Precision@k for specs', 'Precision@k for reviews', 'Precision@k for reviews (product level)'])
    print("Recall@k")
    print(recalls_df.to_string(index=False))
    # print()
    # print("Precision@k")
    # print(precisions_df)
    