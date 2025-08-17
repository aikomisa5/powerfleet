from sqlalchemy.orm import Session
from app.models import Car


def get_car(db: Session, id: str):
    return db.query(Car).filter(Car.id == id).first()

def get_cars(db: Session, filters: dict = None):
    query = db.query(Car)

    if filters:
        if "id_brand" in filters:
            query = query.filter(Car.id_brand == filters["id_brand"])
        if "model" in filters:
            query = query.filter(Car.model == filters['model'])
        if "model__contains" in filters:
            query = query.filter(Car.model.ilike(f"%{filters['model__contains']}%"))

    return query.all()

def post_car(db: Session, id_brand: int, model: str):
    try:
        new_car = Car(id_brand= id_brand, model= model)
        db.add(new_car)
        db.commit()
        db.refresh(new_car)
        return new_car
    except Exception as e:
        db.rollback()
        raise e
