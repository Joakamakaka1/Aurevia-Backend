from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.db.models.country import Country
from app.schemas.country import CountryCreate, CountryUpdate

def get_all_countries(db: Session) -> list[Country]:
    return db.query(Country).all()

def get_country_by_name(db: Session, name: str) -> Country | None:
    """
    
    ** Obtener un país por su nombre **

    - Filtramos la tabla de Country por nombre verificando que coincida 
    con el nombre indicado por parámetro

    """
    return db.query(Country).filter(Country.name == name).first()

def get_country_by_id(db: Session, country_id: int) -> Country | None:
    """

    ** Obtener un país por su ID **

    - Filtramos la tabla de Country por ID verificando que coincida 
    con el ID indicado por parámetro

    """
    return db.query(Country).filter(Country.id == country_id).first()

def validate_country_name_length(name: str) -> None:
    """Valida longitud del nombre del país"""
    if len(name) < 2:
        raise AppError(400, "NAME_TOO_SHORT", "El nombre del país debe tener al menos 2 caracteres")
    if len(name) > 100:
        raise AppError(400, "NAME_TOO_LONG", "El nombre del país no puede tener más de 100 caracteres")

def create_country(db: Session, country_in: CountryCreate) -> Country:
    """
    
    ** Crear un nuevo país **

    - Asignamos el nombre indicado por parámetro a la propiedad name del objeto Country

    """
    try:
        # Validar nombre duplicado
        if get_country_by_name(db, country_in.name):
            raise AppError(409, "COUNTRY_ALREADY_EXISTS", "El país ya existe")
        
        # Validar longitud del nombre (también validado en schema, pero mantenemos por si acaso)
        validate_country_name_length(country_in.name)
        
        country = Country(name=country_in.name)
        db.add(country)
        db.commit()
        db.refresh(country)
        return country
        
    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))

def update_country(db: Session, country_id: int, country_in: CountryUpdate) -> Country:
    """

    ** Actualiza un país por su ID **

    - Seleccionamos el país que se desea actualizar
    - Si no lo encuentra, se lanza un error
    - Si lo encuentra, se actualiza
    
    """
    try:
        # Reutilizar get_country_by_id
        country = get_country_by_id(db, country_id)
        if not country: 
            raise AppError(404, "COUNTRY_NOT_FOUND", "El país no existe")
        
        # Convertir a dict solo con campos no-None
        country_data = country_in.model_dump(exclude_unset=True)
        
        # Validar nombre duplicado si se está actualizando (excluyendo el mismo país)
        if 'name' in country_data and country_data['name'] is not None:
            existing_country = get_country_by_name(db, country_data['name'])
            if existing_country and existing_country.id != country_id:
                raise AppError(409, "COUNTRY_ALREADY_EXISTS", "El país ya existe")
            
            # Validar longitud del nombre
            validate_country_name_length(country_data['name'])
        
        # Actualizar solo campos no-None
        for key, value in country_data.items():
            if value is not None:
                setattr(country, key, value)
        
        db.commit()
        db.refresh(country)
        return country

    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))

def delete_country(db: Session, country_id: int) -> None:
    """

    ** Borra un país por su ID **

    - Seleccionamos el país que se desea eliminar
    - Si no lo encuentra, se lanza un error
    - Si lo encuentra, se elimina

    """
    try:
        # Reutilizar get_country_by_id
        country = get_country_by_id(db, country_id)
        if not country:
            raise AppError(404, "COUNTRY_NOT_FOUND", "El país no existe")
        
        db.delete(country)
        db.commit()
        return None

    except Exception as e:
        db.rollback()
        raise AppError(500, "INTERNAL_SERVER_ERROR", str(e))
