from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter()


# Redirect to Swagger documentation
@router.get("/", include_in_schema=False, operation_id="redirect_page")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")
