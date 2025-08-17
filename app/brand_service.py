from sqlalchemy.orm import Session
from app.models import Brand


def get_brand(db: Session, id: str):
    return db.query(Brand).filter(Brand.id == id).first()

def get_brands(db: Session, filters: dict = None):
    query = db.query(Brand)

    if filters:
        if "name" in filters:
            query = query.filter(Brand.name == filters["name"])

    return query.all()

def post_brand(db: Session, name: str):
    try:
        new_brand = Brand(name=name)
        db.add(new_brand)
        db.commit()
        db.refresh(new_brand)
        return new_brand
    except Exception as e:
        db.rollback()
        raise e