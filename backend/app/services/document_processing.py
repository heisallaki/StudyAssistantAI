import io
import logging

from pypdf import PdfReader
from pypdf.errors import PdfReadError

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".md"}
TEXT_EXTENSIONS = {".txt", ".md"}


def get_extension(filename: str) -> str:
    if "." not in filename:
        return ""
    return "." + filename.rsplit(".", 1)[-1].lower()


def extract_text(file_bytes: bytes, extension: str) -> tuple[str | None, str | None]:
    if extension == ".pdf":
        return _extract_pdf_text(file_bytes)
    if extension in TEXT_EXTENSIONS:
        return _extract_plain_text(file_bytes)
    return None, "Unsupported file type"


def _extract_pdf_text(file_bytes: bytes) -> tuple[str | None, str | None]:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages_text = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n".join(pages_text).strip()
    except (PdfReadError, ValueError, KeyError) as error:
        logger.warning("Failed to parse PDF during text extraction: %s", error)
        return None, "Unable to read this PDF file"

    if not full_text:
        return None, "No extractable text found in this PDF"

    return full_text, None


def _extract_plain_text(file_bytes: bytes) -> tuple[str | None, str | None]:
    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        try:
            text = file_bytes.decode("latin-1")
        except UnicodeDecodeError as error:
            logger.warning("Failed to decode text file: %s", error)
            return None, "Unable to decode this text file"

    text = text.strip()
    if not text:
        return None, "This file appears to be empty"

    return text, None