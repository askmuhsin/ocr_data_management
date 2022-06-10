from docarray import Document, DocumentArray
from jina import Executor, Flow, requests

import os
import numpy as np

def print_matches(req):
    for idx, d in enumerate(req.docs[0].matches[:3]):
        print(f'[{idx}]{d.scores["euclid"].value:2f}: "{d.text}"')

class CharEmbed(Executor):
    offset = 32
    dim = 127 - offset + 1
    char_embd = np.eye(dim) * 1

    @requests
    def foo(self, docs: DocumentArray, **kwargs):
        for d in docs:
            r_emb = [ord(c) - self.offset if self.offset <= ord(c) <= 127 else (self.dim - 1) for c in d.text]
            d.embedding = self.char_embd[r_emb, :].mean(axis=0)


class Indexer(Executor):
    _docs = DocumentArray()

    @requests(on='/index')
    def foo(self, docs: DocumentArray, **kwargs):
        self._docs.extend(docs)

    @requests(on='/search')
    def bar(self, docs: DocumentArray, **kwargs):
        docs.match(self._docs, metric='euclidean', limit=20)


def define_flow():
    flow = (
        Flow()
        .add(uses=CharEmbed, replicas=1)
        .add(uses=Indexer, shards=1)
    )
    return flow


def main():
    flow = define_flow()
    flow.plot('flow.svg')
    
    sample_text = [
        "sample text 1",
        "text about airlines",
        "something else about mac"
    ]

    da = DocumentArray(
        [
            Document(text=x) 
            for x in sample_text
        ]
    )
    with flow:
        flow.index(da)
        flow.search(Document(text='mac'), on_done=print_matches)

if __name__=='__main__':
    main()
