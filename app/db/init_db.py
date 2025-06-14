from sqlalchemy.orm import Session

from app.db.base_class import Base
from app.db.session import engine
from app.core.config import settings

def init_db() -> None:
    # Cria todas as tabelas
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    print("Criando tabelas do banco de dados...")
    init_db()
    print("Tabelas criadas com sucesso!") 