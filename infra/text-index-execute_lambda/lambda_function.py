import json
from jina import Client
from docarray import Document, DocumentArray

def lambda_handler(event, context):
    print(event)

    c = Client(
        protocol='http', 
        host='ec2-3-83-123-10.compute-1.amazonaws.com',
        port=12345,
    )
    doc_text = "null"

    if 'Records' in event:
        body = eval(event['Records'][0]['body'])
        text_to_index = body['text']
        s3_obj_key = body['s3_object_key']

        text_body = [text_to_index]
        da = DocumentArray(
            [
                Document(text=x, s3_obj_key=s3_obj_key) 
                for x in text_body
            ]
        )
        doc_text = da[0].text
        print(f"Document text -- {doc_text}; tags -- {da[0].tags}")
        c.index(da)
        
    return {
        'statusCode': 200,
        'text': doc_text,
    }
