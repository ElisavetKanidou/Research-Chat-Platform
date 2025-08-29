# backend/app/db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings

# Δημιουργεί τη "μηχανή" της SQLAlchemy που συνδέεται με τη βάση δεδομένων
# Το connect_args είναι ειδικά για SQLite, αλλά το αφήνουμε για συμβατότητα
# Για PostgreSQL, η κύρια ρύθμιση είναι το DATABASE_URL
engine = create_engine(
    settings.DATABASE_URL
)

# Δημιουργεί ένα "εργοστάσιο" για database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Μια βασική κλάση από την οποία θα κληρονομήσουν όλα τα μοντέλα της βάσης (ORM models)
Base = declarative_base()

# Dependency function για το FastAPI: Παρέχει ένα database session σε κάθε request
# και εξασφαλίζει ότι θα κλείσει σωστά στο τέλος.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()