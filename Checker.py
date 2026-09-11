from database import SessionLocal
from models import Material

db = SessionLocal()
materials = db.query(Material).all()
print(materials)
