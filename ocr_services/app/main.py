import secrets
from typing import Union

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()

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
