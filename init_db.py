# from database import Base, engine
#
# print("Creating tables...")
# Base.metadata.create_all(bind=engine)
# print("Tables created successfully!")


from database import Base, engine
from models import *

def init_db():
    Base.metadata.create_all(bind=engine)
