import secrets
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .models.paddle_ocr import PaddleOCRModel
from .utils import get_image_from_url

app = FastAPI()
security = HTTPBasic()

ocr_model = PaddleOCRModel()
ocr_model.inspect_output = False

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
    return {"Hello": "World"}

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
def ocr_infer_paddle(
    image_links
):
    image = get_image_from_url(image_link)
    ocr_model.predict(image)
    return {
        'text': ocr_model.processed_output['stitched_text']
    }

