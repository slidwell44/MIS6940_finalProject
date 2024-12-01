from src import app, logger

from src.routes import redirect_router, workorder_router

app.include_router(redirect_router)
app.include_router(workorder_router)

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting...")
    uvicorn.run("src.main:app", host="localhost", port=7070, reload=True)
