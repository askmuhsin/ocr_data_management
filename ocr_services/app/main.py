import secrets
import numpy as np
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .models.paddle_ocr import PaddleOCRModel
from .utils import (
    get_image_from_url, get_image_from_s3, 
    write_annotated_file_to_s3,
    write_to_sqs,
)

app = FastAPI()
security = HTTPBasic()

ocr_model = PaddleOCRModel()
ocr_model.inspect_output = True
ocr_model.debug = False

def get_current_username(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "ocr_admin")
    correct_password = secrets.compare_digest(credentials.password, "ocr_1234")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


@app.get("/")
def read_root():
    return {"name": "ocr_service"}


@app.get("/items/{item_id}")
def read_item(
    item_id: int, 
    q: Union[str, None] = None,
    username: str = Depends(get_current_username),
):
    return {
        "item_id": item_id, 
        "q": q,
        "username": username, 
    }


@app.get("/infer/paddleOCR/")
def ocr_infer_url(
    image_link
):
    image = get_image_from_url(image_link)
    ocr_model.predict(image)
    return {
        'text': ocr_model.processed_output['stitched_text']
    }

@app.post("/v1/ocr_service_run/")
def ocr_service_run(s3_object_key, s3_bucket='ocr-requested-images'):
    print('[INFO] Read Image from S3 ... ')
    img = get_image_from_s3(s3_object_key, s3_bucket)

    if isinstance(img, np.ndarray):
        print(f'[INFO] retrivied image of type {type(img)} and shape {img.shape}')
    else:
        print(f'[ERROR] invalid image type -- {type(img)}')

    print('[INFO] Run Inference ... ')
    ocr_model.predict(img)
    print(f"[INFO] Inferred text -- {ocr_model.processed_output['stitched_text']}")

    print('[INFO] write inspect image to S3 ... ')
    write_annotated_file_to_s3(ocr_model.pred_annotated_img, s3_object_key)

    print('[INFO] writing text to SQS for indexing ... ')
    sqs_response = write_to_sqs(
        ocr_model.processed_output['stitched_text'], s3_object_key
    )
    print(f'[INFO] sqs response -- {sqs_response}')

    return {
        'text': ocr_model.processed_output['stitched_text'],
        's3_object_key': s3_object_key,
    }
