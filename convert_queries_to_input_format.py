import json

with open('/home/miyoung/suehyun/DPR/input/retriever/reddit/val_sample_annotated_v1.json', 'r') as f:
    queries = json.load(f)

topics = {}

for query in queries:
    id = int(query["num"])
    content = f'title: {query["q_title"]}\nbody: {query["q_body"]}'
    topics[id] = {"title": content}

with open('input/retriever/reddit/val_sample_annotated_v1_pyserini.json', 'w') as f:
    json.dump(topics, f, indent=4)