from src import app
from src.routes.api import api_router
from src.routes.change_overlay import change_overlay_router
from src.routes.server import server_router

# Add routes
app.include_router(api_router)
app.include_router(change_overlay_router)
app.include_router(server_router, prefix="/Server")

# TODO: Fix these error messages:
#   W:\python_modules\venvs\test\fastapi_venv\Lib\site-packages\fastapi\openapi\utils.py:207: UserWarning: Duplicate Operation ID pdf_change_overlay for function get_overlay at C:\Users\sl3789\PycharmProjects\engineeringservicesfastapi\src\routes\change_overlay\routes\change_overlay_route.py
#   warnings.warn(message, stacklevel=1)
#   W:\python_modules\venvs\test\fastapi_venv\Lib\site-packages\fastapi\openapi\utils.py:207: UserWarning: Duplicate Operation ID health_check_server for function health_check at C:\Users\sl3789\PycharmProjects\engineeringservicesfastapi\src\routes\server\routes\server_route.py
#   warnings.warn(message, stacklevel=1)
#   W:\python_modules\venvs\test\fastapi_venv\Lib\site-packages\fastapi\openapi\utils.py:207: UserWarning: Duplicate Operation ID system_stats_server for function system_stats at C:\Users\sl3789\PycharmProjects\engineeringservicesfastapi\src\routes\server\routes\server_route.py
#   warnings.warn(message, stacklevel=1)

# Run the application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="wimesprodsrv", port=8000, workers=4)
    # uvicorn.run("src.main:app", host="localhost", port=8023, reload=False)
