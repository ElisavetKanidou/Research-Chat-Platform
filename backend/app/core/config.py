# backend/app/core/config.py

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Διαχειρίζεται τις ρυθμίσεις της εφαρμογής και τις μεταβλητές περιβάλλοντος.
    """
    DATABASE_URL: str

    class Config:
        # Ορίζει το αρχείο από το οποίο θα διαβαστούν οι μεταβλητές
        env_file = ".env"

# Δημιουργείται ένα μοναδικό instance που θα χρησιμοποιείται σε όλη την εφαρμογή
settings = Settings()