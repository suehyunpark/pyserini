# largely adapted from https://github.com/openai/chatgpt-retrieval-plugin/blob/main/services/chunks.py

from argparse import ArgumentParser
# from transformers import LlamaTokenizerFast
import json

from pathlib import Path
from tqdm import tqdm

CHUNK_SIZE = 200  # tokens
MIN_CHUNK_LEN = 5  # chars

# tokenizer = LlamaTokenizerFast.from_pretrained("/checkpoints/llama-7b-hf")


class DocConvertor:  # previous version, need to fix title mapping
    def __init__(self, source_type: str):
        self.source_type = source_type
        self.id_field = "doc_id"
        self.title_field = "title"
        self.body_field = "body"
        self.delimiter = "<DL>"
        self.special_field = "product" if "review" in source_type else None
    
    def convert_doc(self, orig_doc: dict):
        title = orig_doc[self.title_field].strip()
        body = orig_doc[self.body_field].replace("\n", " ").strip()
        if self.special_field:
            title += f"\n{orig_doc[self.special_field]}"
        return {
            "id": orig_doc[self.id_field],
            "contents": title + self.delimiter + body
        }
        

class DocChunker(DocConvertor):  # not used now
    def __init__(self, source_type: str, chunk_token_size: int=None):
        super().__init__(source_type)
        self.chunk_token_size = chunk_token_size if chunk_token_size else CHUNK_SIZE
      
    def get_text_chunks(self, text: str):
        tokens = tokenizer.encode(text, add_special_tokens=False)
        chunks = []
        
        while tokens:
            chunk = tokens[:self.chunk_token_size]
            chunk_text = tokenizer.decode(chunk)
            # Skip the chunk if it is empty or whitespace
            if not chunk_text or chunk_text.isspace():
                # Remove the tokens corresponding to the chunk text from the remaining tokens
                tokens = tokens[len(chunk):]
                continue
            
            # Find the last period or punctuation mark in the chunk
            last_punctuation = max(
                chunk_text.rfind("."),
                chunk_text.rfind("?"),
                chunk_text.rfind("!"),
                chunk_text.rfind("\n"),
            )
            
            if last_punctuation != -1:
                chunk_text = chunk_text[:last_punctuation + 1]
            chunk_text_to_append = chunk_text.replace("\n", " ").strip()
            
            if len(chunk_text_to_append) > MIN_CHUNK_LEN:
                chunks.append(chunk_text_to_append)
            # Remove the tokens corresponding to the chunk text from the remaining tokens
            tokens = tokens[len(tokenizer.encode(chunk_text, add_special_tokens=False)):]
        
        if tokens:
            remaining_text = tokenizer.decode(tokens).replace("\n", " ").strip()
            if len(remaining_text) > MIN_CHUNK_LEN:
                chunks.append(remaining_text)
                
        return chunks
    
        
    def convert_doc_to_chunks(self, orig_doc: dict):
        doc_id = orig_doc[self.id_field]
        title = orig_doc[self.title_field]
        if self.special_field:
            title += f"\n{orig_doc[self.special_field]}"
        body = orig_doc[self.body_field]
        text_chunks = self.get_text_chunks(body)
        
        for i, chunk in enumerate(text_chunks):
            chunk_id = f"{doc_id}_{i}"
            yield {
                "id": chunk_id,
                "contents": title + self.delimiter + chunk
            }
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source-type", required=True, choices=["reddit", "cc", "amazon-specs", "amazon-review"], help="source type of input files")
    parser.add_argument("--chunk-token-size", type=int, help="chunk size in tokens")
    parser.add_argument("--input-file-path", required=True)
    parser.add_argument("--output-file-path", required=True)
    args = parser.parse_args()
    
    input_file_path = Path(args.input_file_path)
    output_file_path = Path(args.output_file_path)
    output_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if args.chunk_token_size:
        doc_convertor = DocChunker(args.source_type, args.chunk_token_size)
        writer = open(output_file_path, 'w')
        with open(input_file_path, 'r') as f:
            for line in tqdm(f):
                orig_doc = json.loads(line)
                for chunked_doc in doc_convertor.convert_doc_to_chunks(orig_doc):
                    writer.write(json.dumps(chunked_doc) + '\n')
        writer.close()
    else:
        doc_convertor = DocConvertor(args.source_type)
        writer = open(output_file_path, 'w')
        with open(input_file_path, 'r') as f:
            for line in tqdm(f):
                orig_doc = json.loads(line)
                converted_doc = doc_convertor.convert_doc(orig_doc)
                writer.write(json.dumps(converted_doc) + '\n')
        writer.close()