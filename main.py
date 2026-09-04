from fastapi import FastAPI
from error_handlers import register_error_handlers
from routers import router

app = FastAPI(
    title="FastAPI Backend by Koni",
    description="""
    🚀 This backend was developed by Koni using FastAPI.
    It includes custom error handling and modular routing.
    """,
    version="0.1.0",
    contact={
        "name": "Koni",
        "email": "konikakraba0@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

register_error_handlers(app)
app.include_router(router)

