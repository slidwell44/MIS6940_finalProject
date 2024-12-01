from fastapi import APIRouter, UploadFile, Response
from fastapi.responses import StreamingResponse
import logging

from src.routes.change_overlay.services import change_overlay

router = APIRouter(
    tags=["Change Overlay"]
)

logger = logging.getLogger(__name__)


@router.post("/PDF_Overlay/", operation_id="pdf_change_overlay")
async def get_overlay(file1: UploadFile, file2: UploadFile) -> Response:
    try:
        logger.info(f"File1 type: {file1.content_type}, File2 type: {file2.content_type}")

        pdf = await change_overlay(file1, file2)
        pdf.seek(0)

        def iter_pdf(file_object, chunk_size=1024 * 1024):
            while chunk := file_object.read(chunk_size):
                yield chunk

        headers = {'Content-Disposition': 'attachment; filename="out.pdf"'}

        return StreamingResponse(iter_pdf(pdf), media_type="application/pdf", headers=headers)
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response(content=f"Internal server error: {str(e)}", status_code=500)
