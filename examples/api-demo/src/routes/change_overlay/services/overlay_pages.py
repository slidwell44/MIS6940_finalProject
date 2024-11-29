import pymupdf as fitz
import logging
from .path_to_shapes import path_to_shapes


def copy_pdf_with_vector_lines(file_data):
    file1_data, file2_data, i = file_data
    new_doc = fitz.open()
    doc1 = fitz.open(stream=file1_data, filetype="pdf")
    doc2 = fitz.open(stream=file2_data, filetype="pdf")
    o = doc1.load_page(i) if i < doc1.page_count else None
    n = doc2.load_page(i) if i < doc2.page_count else None
    if o and n:
        old = o.get_drawings()
        new = n.get_drawings()
        new_page = new_doc.new_page(width=o.rect.width, height=o.rect.height)
        path_to_shapes(new_page, old, (215/255, 0, 0), opacity=0.7)
        path_to_shapes(new_page, new, (0, 64/255, 0), opacity=0.7)
    elif o and not n:
        old = o.get_drawings()
        new_page = new_doc.new_page(width=o.rect.width, height=o.rect.height)
        path_to_shapes(new_page, old, (215/255, 0, 0), opacity=0.7)
    elif not o and n:
        new = n.get_drawings()
        new_page = new_doc.new_page(width=n.rect.width, height=n.rect.height)
        path_to_shapes(new_page, new, (0, 64/255, 0), opacity=0.7)
    b = new_doc.tobytes()
    new_doc.close()
    return b
