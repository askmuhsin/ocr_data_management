from docarray import Document, DocumentArray
from jina import Executor, Flow, requests

import os

def print_results(resp, limit=3):
    print('QUERY : ', resp.contents)
    for docs in resp.traverse('m'):
        for n, doc in enumerate(docs[:limit]):
            print(n)
            print('\t', doc.scores.get('cosine').value)
            print('\t', doc.text)
            print()


class SimpleIndexer(Executor):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        print(os.path.join(self.workspace, 'index.db'))
        self._index = DocumentArray(
            storage='sqlite',
            config={
                'connection': os.path.join(self.workspace, 'index.db'),
                'table_name': 'bert_base_uncased',
            },
        )

    @requests(on='/index')
    def index(self, docs: DocumentArray, **kwargs):
        self._index.extend(docs)

    @requests(on='/search')
    def search(self, docs: DocumentArray, **kwargs):
        docs.match(self._index)
        
        
def define_flow():
    flow = (
        Flow(
            port_expose=12345, 
            protocol='http', 
            cors=True,
            title='Text Search',
            description='Simple search on `text`',
        )
        .add(
            uses='jinahub+docker://TransformerTorchEncoder',
            uses_with={'pretrained_model_name_or_path': 'bert-base-uncased'},
            volumes='.cache/huggingface:/root/.cache/huggingface',
        )
        .add(uses=SimpleIndexer, name='indexer', workspace='workspace')
    )
    return flow


def main():
    flow = define_flow()
    flow.plot('flow.svg')
    
    with flow:
        # flow.to_docker_compose_yaml('docker-compose.yml')
        # flow.block()
        print(flow)
        

if __name__=='__main__':
    main()
