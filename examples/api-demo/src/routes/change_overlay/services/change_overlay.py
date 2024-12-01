import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor
# from multiprocessing import Pool
from fastapi import UploadFile
from io import BytesIO
import pymupdf as fitz
from functools import partial

from .overlay_pages import copy_pdf_with_vector_lines
from .path_to_shapes import path_to_shapes


async def change_overlay(file1: UploadFile, file2: UploadFile) -> BytesIO:
    loop = asyncio.get_running_loop()

    # Read both files
    file1_data = await file1.read()
    file2_data = await file2.read()
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # Check PDF lengths

    new_doc = fitz.open()
    doc1 = fitz.open(stream=file1_data, filetype="pdf")
    doc2 = fitz.open(stream=file2_data, filetype="pdf")

    # Use ProcessPoolExecutor for parallel processing
    process_func = partial(copy_pdf_with_vector_lines)

    with ProcessPoolExecutor() as executor:
        tasks = []
        for i in range(max(doc1.page_count, doc2.page_count)):
            tasks.append(loop.run_in_executor(executor, process_func, (file1_data, file2_data, i)))
        results = await asyncio.gather(*tasks)
    for r in results:
        page_pdf = fitz.open("pdf", r)
        new_doc.insert_pdf(page_pdf)

    logger.info("Outputting change overlay")
    return BytesIO(new_doc.tobytes())
