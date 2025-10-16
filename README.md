python -m venv venv // Entorno virtual
pip install fastapi uvicorn // Instalar las dependencias de FastAPI y Uvicorn
pip install mysql-connector-python // Instalar MySQL Connector/Python
pip install "pydantic[email]" // Instalar Pydantic con el módulo email
pip install sqlalchemy // Instalar SQLAlchemy
pip install passlib // Instalar passlib
uvicorn app.main:app // Iniciar el servidor Uvicorn
uvicorn main:app --reload // Iniciar el servidor Uvicorn con recarga automática
