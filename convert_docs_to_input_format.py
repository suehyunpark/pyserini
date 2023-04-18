import json
from pathlib import Path
from argparse import ArgumentParser


class DocConvertor:
    def __init__(
        self, 
        source_type: str, 
        id_field: str="doc_id", 
        title_field: str="title", 
        body_field: str="body",
        delimiter: str="<DL>"
    ):
        self.input_fields = ["id", "contents"]
        self.source_type = source_type
        self.id_field = id_field
        self.title_field = title_field
        self.body_field = body_field
        self.delimiter = delimiter
    
    def add_extra_field(self, field: str):
        self.extra_field = field
        
    def remove_extra_field(self):
        self.extra_field = None
    
    def convert_doc(self, orig_doc: dict):
        title = orig_doc[self.title_field]
        body = orig_doc[self.body_field]
        if self.extra_field:
            body = orig_doc[self.extra_field] + '\n' + body
        return {
            "id": orig_doc[self.id_field],
            "contents": title + self.delimiter + body
        }
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source-type", required=True, choices=["reddit", "cc", "amazon"], help="source type of input files")
    parser.add_argument("--input-dir", required=True, help="path to input files directory with same source type")
    parser.add_argument("--output-dir", required=True, help="path to output files directory")
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    doc_convertor = DocConvertor(args.source_type)
    for input_path in input_dir.iterdir():
        input_file = input_path.name
        if "review" in input_file:
            doc_convertor.add_extra_field("product")
        writer = open(output_dir / input_file, 'w')
        with open(input_path, 'r') as f:
            for line in f:
                orig_doc = json.loads(line)
                converted_doc = doc_convertor.convert_doc(orig_doc)
                writer.write(json.dumps(converted_doc) + '\n')
        writer.close()
        doc_convertor.remove_extra_field()