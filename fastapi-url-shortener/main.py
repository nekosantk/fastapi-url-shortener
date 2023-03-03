import validators
from . import schemas, models, crud

from starlette.datastructures import URL
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from .config import get_settings

from .database import get_db, engine


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return "Welcome to the FastAPI URL shortener"


@app.get("/admin/{secret_key}", name="Administration information", response_model=schemas.URLInfo)
def get_url_info(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.get_db_url_by_secret(db=db, secret_key=secret_key):
        db_url.url = db_url.key
        db_url.admin_url = db_url.secret_key
        return get_admin_info(db_url)
    else:
        raise_not_found(request)


@app.delete("/admin/{secret_key}")
def delete_url(secret_key: str, request: Request, db: Session = Depends(get_db)):
    if db_url := crud.deactivate_db_url_by_secret_key(db=db, secret_key=secret_key):
        message = f"Successfully deleted shortlink to {db_url.target_url}"
        return {"detail": message}
    else:
        raise_not_found(request)


@app.post("/url", response_model=schemas.URLInfo)
def create(url: schemas.URLBase, db: Session = Depends(get_db)):
    if not validators.url(url.target_url):
        raise_bad_request(message="URL is not valid.")

    db_url = crud.create_db_url(db=db, url=url)
    db_url.admin_url = db_url.secret_key

    return get_admin_info(db_url)


@app.get("/{url_key}")
def forward(url_key: str, request: Request, db: Session = Depends(get_db)):

    if db_url := crud.get_db_url_by_key(db=db, url_key=url_key):
        crud.update_link_clicks(db=db, db_url=db_url)
        return RedirectResponse(db_url.target_url)
    return raise_not_found(request)


def raise_bad_request(message):
    raise HTTPException(status_code=400, detail=message)


def raise_not_found(request):
    message = f"URL '{request.url}' was not found."
    raise HTTPException(status_code=404, detail=message)


def get_admin_info(db_url: models.URL) -> schemas.URLInfo:
    base_url = URL(get_settings().base_url)
    admin_endpoint = app.url_path_for("Administration information", secret_key=db_url.secret_key)
    db_url.url = str(base_url.replace(path=db_url.key))
    db_url.admin_url = str(base_url.replace(path=admin_endpoint))
    return db_url
