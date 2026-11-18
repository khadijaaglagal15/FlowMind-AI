from backend.app.database import engine
from backend.app.models import Base, Sale, RetailTransaction

Base.metadata.create_all(bind=engine)

print("Tables créées ou déjà existantes.")