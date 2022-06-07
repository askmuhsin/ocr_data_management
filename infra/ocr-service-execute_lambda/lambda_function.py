import json
import requests

def lambda_handler(event, context):
    url = 'http://localhost:8123/v1/ocr_service_run'
    print(event)
    
    res = {}
    body, s3_obj_key, s3_bucket_name = None, None, None
    if 'Records' in event:
        body = eval(event['Records'][0]['body'])
        if 'Records' in body:
            s3_obj_key = body['Records'][0]['s3']['object']['key']
            s3_bucket_name = body['Records'][0]['s3']['bucket']['name']
            
            params = {
                's3_object_key': s3_obj_key,
                's3_bucket': s3_bucket_name,
            }
            
            res_ = requests.post(url, params=params)
            res = eval(res_.text)
    
    print(f's3_obj_key -- {s3_obj_key}')
    print(f's3_bucket_name -- {s3_bucket_name}')
    print('+-' * 30)
    
    data = {
        'statusCode': 200,
        'body': json.dumps(f'processed {s3_bucket_name}, {s3_obj_key}')
    }
    data.update(res)
    
    return data

