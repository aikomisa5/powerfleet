from sqlalchemy.orm import Session
from app.models import Picture
from fastapi.responses import StreamingResponse
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from googleapiclient.discovery import build
import io
import re
import os
import json
from dotenv import load_dotenv

load_dotenv()

SERVICE_ACCOUNT_PATH_LOCALHOST = "./etc/secrets/powerfleet-google-service-account.json"
SERVICE_ACCOUNT_PATH_RENDER = "/etc/secrets/powerfleet-google-service-account.json"
ENVIRONMENT = os.getenv("ENVIRONMENT")


def get_drive_service():
    service_account_path = None
    if ENVIRONMENT == "LOCALHOST":
        service_account_path = SERVICE_ACCOUNT_PATH_LOCALHOST
    else:
        service_account_path = SERVICE_ACCOUNT_PATH_RENDER

    if not os.path.exists(service_account_path):
        raise FileNotFoundError(f"Service account file not found at {service_account_path}")

    google_account_service_json = None
    with open(service_account_path, "r") as f:
        google_account_service_json = json.load(f)
    creds = service_account.Credentials.from_service_account_info(google_account_service_json)
    return build("drive", "v3", credentials=creds)

def get_picture_raw(db: Session, id: int):
    filters = {
        "id": id
    }
    pictures = get_pictures(db, filters)
    if len(pictures) == 0:
        raise ValueError(f"Pics not found for filters: {filters}")
    url = pictures[0].url
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', url)
    file_id = match.group(1) if match else None

    if not file_id:
        raise ValueError(f"Invalid Google Drive URL: {url}")

    service = get_drive_service()
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    fh.seek(0)
    return StreamingResponse(fh, media_type="image/jpeg")

def get_pictures(db: Session, filters: dict = None):
    query = db.query(Picture)

    if filters:
        if "id_car" in filters:
            query = query.filter(Picture.id_car == filters["id_car"])
        if "id" in filters:
            query = query.filter(Picture.id == filters["id"])

    return query.all()

def post_picture(db: Session, id_car: int, description: str, url: str):
    try:
        picture = Picture(id_car=id_car, description=description, url=url)
        db.add(picture)
        db.commit()
        db.refresh(picture)
        return picture
    except Exception as e:
        db.rollback()
        raise e
