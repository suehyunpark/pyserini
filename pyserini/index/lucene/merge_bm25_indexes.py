import os
from pyserini.pyclass import autoclass, JPaths, JArray, JClass

# Import Java classes
StandardAnalyzer = autoclass('org.apache.lucene.analysis.standard.StandardAnalyzer')
IndexWriterConfig = autoclass('org.apache.lucene.index.IndexWriterConfig')
FSDirectory = autoclass('org.apache.lucene.store.FSDirectory')
IndexWriter = autoclass('org.apache.lucene.index.IndexWriter')
TieredMergePolicy = autoclass('org.apache.lucene.index.TieredMergePolicy')
Directory = autoclass('org.apache.lucene.store.Directory')


def merge_indexes(source_directories, merged_index_path):
    # Create a new empty index directory
    merged_index_dir = FSDirectory.open(JPaths.get(os.path.abspath(merged_index_path)))

    # Set up the index writer configuration
    analyzer = StandardAnalyzer()
    config = IndexWriterConfig(analyzer)

    # Optional: Customize merge policy
    merge_policy = TieredMergePolicy()
    # Set merge policy configurations if needed
    # merge_policy.setXXX(...)
    config.setMergePolicy(merge_policy)

    # Create the index writer
    merged_index_writer = IndexWriter(merged_index_dir, config)

    # Merge the source indexes into the new merged index
    source_directories = [FSDirectory.open(JPaths.get(os.path.abspath(p))) for p in source_directories]
    source_directories_java_array = JArray.newInstance(Directory, len(source_directories))
    for i, directory in enumerate(source_directories):
        JArray.set(source_directories_java_array, i, directory)
    directory_array_class = Directory.getClassLoader().loadClass("[Lorg.apache.lucene.store.Directory;")
    source_directories_java_array = directory_array_class.cast(source_directories_java_array)
    merged_index_writer.addIndexes(source_directories_java_array)

    # Commit the changes and close the writer
    merged_index_writer.commit()
    merged_index_writer.close()


if __name__ == '__main__':
    source_index_paths = [
        'indexes/amazon/v2/bm25',
        'indexes/cc/bm25',
        'indexes/reddit/bm25'
    ]

    merged_index_path = 'indexes/combined/bm25'

    merge_indexes(source_index_paths, merged_index_path)
