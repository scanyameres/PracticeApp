"""Turn an uploaded CV (PDF) into plain text for the LLM prompt.

Like web_fetch.py for URLs: the app converts the input to text itself, so the LLM only ever
receives text. Uses pypdf, which reads the text layer of the PDF.

Public function: read_pdf_text().
"""

from typing import BinaryIO

from pypdf import PdfReader
from pypdf.errors import PdfReadError

# Below this, the PDF is probably a scan (an image of a CV) with no text layer.
MIN_CHARS = 50


def read_pdf_text(file: BinaryIO) -> str:
    """Return the text of all pages of the PDF in `file` (any binary file-like object).

    Raises:
        ValueError: if the file is not a readable PDF or contains (almost) no text.
    """
    try:
        reader = PdfReader(file)
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except PdfReadError as error:
        raise ValueError(f"Could not read this PDF ({error}). Please paste your CV instead.") from error

    if len(text) < MIN_CHARS:
        raise ValueError(
            "Could not find text in this PDF (it may be a scanned image). Please paste your CV instead."
        )
    return text
