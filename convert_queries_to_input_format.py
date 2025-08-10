import json

with open('/home/miyoung/suehyun/DPR/input/retriever/reddit/reddit-val-v3-sampled.json', 'r') as f:
    queries = json.load(f)

topics = {}

for query in queries:
    id = int(query["num"])
    content = f'title: {query["q_title"]}\nbody: {query["q_body"]}'
    topics[id] = {"title": content}

with open('input/retriever/reddit/reddit-val-v3-sampled_pyserini.json', 'w') as f:
    json.dump(topics, f, indent=4)