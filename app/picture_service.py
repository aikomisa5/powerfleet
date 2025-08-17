from sqlalchemy.orm import Session
from app.models import Picture

def get_pictures(db: Session, filters: dict = None):
    query = db.query(Picture)

    if filters:
        if "id_car" in filters:
            query = query.filter(Picture.id_car == filters["id_car"])

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
