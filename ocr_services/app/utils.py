from docarray import Document, DocumentArray
from urllib.request import urlopen, Request
from jina import Client
import numpy as np
import shutil
import boto3
import json
import cv2
import io
import os

header = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'none',
    'Accept-Language': 'en-US,en;q=0.8',
    'Connection': 'keep-alive'
}

def get_image_from_url(url):
    req = Request(url)
    req.headers = header
    content = urlopen(req).read()
    
    arr = np.asarray(bytearray(content), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    return img


def get_image_from_s3(
    s3_object_key, s3_bucket, region_name='us-east-1'):
    img = None
    try:
        s3 = boto3.resource(
            's3',
            region_name=region_name,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        ocr_request_bucket = s3.Bucket(s3_bucket)
        img_obj = ocr_request_bucket.Object(s3_object_key)

        local_file_path = os.path.join('/tmp', s3_object_key)
        dir_path = os.path.dirname(local_file_path)
        os.makedirs(dir_path,exist_ok=True)

        img_obj.download_file(local_file_path)

        img = cv2.imread(local_file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    except Exception as e:
        print('[ERROR] get_image_from_s3 : ', s3_object_key, s3_bucket, e)
    else:
        shutil.rmtree(dir_path)
    
    return img


def write_annotated_file_to_s3(
    pred_annotated_img, s3_object_key, 
    s3_bucket='ocr-output-images', region_name='us-east-1'):
    try:
        s3 = boto3.resource(
            's3',
            region_name=region_name,
            aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        )
        ocr_output_bucket = s3.Bucket(s3_bucket)
        # img_obj = ocr_output_bucket.Object(s3_object_key)

        pred_annotated_img = cv2.cvtColor(pred_annotated_img, cv2.COLOR_RGB2BGR)

        local_file_path = os.path.join('/tmp/output', s3_object_key)
        dir_path = os.path.dirname(local_file_path)
        os.makedirs(dir_path, exist_ok=True)

        cv2.imwrite(local_file_path, pred_annotated_img)
        
        print(f'[INFO] writing {local_file_path} to {s3_object_key} in {s3_bucket}')
        ocr_output_bucket.upload_file(local_file_path, s3_object_key)
    except Exception as e:
        print('[ERROR] write_annotated_file_to_s3 : ', s3_object_key, e)
    else:
        shutil.rmtree(dir_path)


def write_to_sqs(
    text, s3_object_key, 
    queue_name='text-index-requests', 
    region_name='us-east-1'):

    sqs = boto3.resource(
        'sqs',
        region_name=region_name,
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    )
    text_index_request_queue = sqs.get_queue_by_name(QueueName=queue_name)
    message = {
        "text": text,
        "s3_object_key": s3_object_key,
    }
    message_text = json.dumps(message)
    try:
        response = text_index_request_queue.send_message(MessageBody=message_text)
    except Exception as e:
        print(f'[ERROR] write_to_sqs : {queue_name}', e)
    return response


def index_to_jina(text_to_index, s3_object_key):
    c = Client(
        protocol='http', 
        host='ec2-3-83-123-10.compute-1.amazonaws.com',
        port=12345,
    )
    text_to_index = text_to_index if isinstance(text_to_index, list) else [text_to_index]

    da = DocumentArray(
        [
            Document(text=x, s3_object_key=s3_object_key) 
            for x in text_to_index
        ]
    )
    doc_text = da[0].text
    print(f"Document text -- {doc_text}; tags -- {da[0].tags}")
    c.index(da)

    return doc_text
