from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.db.models.country import Country

def get_all_countries(db: Session) -> list[Country]:
    return db.query(Country).all()

def get_country_by_name(db: Session, name: str) -> Country | None:
    """
    
    ** Obtener una ciudad por su nombre **

    - Filtramos la tabla de Country por nombre verificando que coincida 
    con el nombre indicado por parámetro

    """
    return db.query(Country).filter(Country.name == name).first()

def create_country(db: Session, name: str) -> Country:
    """
    
    ** Crear una nueva ciudad **

    - Asignamos el nombre indicado por parámetro a la propiedad name del objeto COUNTRY

    """
    country = Country(name = name)
    db.add(country)
    db.commit()
    db.refresh(country)
    return country

def update_country_by_name(db: Session, name: str) -> Country:
    """

    ** Actualiza una ciudad por su nombre **

    - Seleccionamos la ciudad que se desea actualizar
    - Si no la encuentra, se lanza un error
    - Si la encuentra, se actualiza el nombre
    
    """
    country = get_country_by_name(db, name)

    if not country: 
        raise AppError(404, "COUNTRY NOT FOUND", "Country not found")
    
    country.name = name
    db.commit()
    db.refresh(country)
    return country

def delete_country_by_name(db: Session, name: str) -> None:
    """

    ** Borra una ciudad por su nombre **

    - Seleccionamos la ciudad que se desea eliminar
    - Si no la encuentra, se lanza un error
    - Si la encuentra, se elimina

    """
    country = db.query(Country).filter(Country.name == name).first()

    if not country:
        raise AppError(404, "COUNTRY NOT FOUND", "Country not found")
    
    db.delete(country)
    db.commit()
    return None
