from fastapi import FastAPI
from fastapi.openapi.docs import get_redoc_html
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
    docs_url="/docs",
    redoc_url=None  # disable default ReDoc so we can override it
)

# Custom ReDoc page


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="FastAPI Backend by Koni",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js",
        with_google_fonts=True
    )


register_error_handlers(app)
app.include_router(router)
