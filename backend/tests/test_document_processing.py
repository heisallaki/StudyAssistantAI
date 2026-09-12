import io

from app.services import document_processing


def _build_pdf_with_text(text: str) -> bytes:
    content = f"BT /F1 24 Tf 72 700 Td ({text}) Tj ET".encode()
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        b"/Resources<</Font<</F1 5 0 R>>>>/Contents 4 0 R>>",
        b"<</Length " + str(len(content)).encode() + b">>stream\n" + content + b"\nendstream",
        b"<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>",
    ]

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(buf.tell())
        buf.write(f"{index} 0 obj".encode() + obj + b"endobj\n")
    xref_offset = buf.tell()
    buf.write(f"xref\n0 {len(objects) + 1}\n".encode())
    buf.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buf.write(f"{offset:010} 00000 n \n".encode())
    buf.write(b"trailer<</Size " + str(len(objects) + 1).encode() + b"/Root 1 0 R>>\n")
    buf.write(b"startxref\n" + str(xref_offset).encode() + b"\n%%EOF")
    return buf.getvalue()


def _build_blank_pdf() -> bytes:
    objects = [
        b"<</Type/Catalog/Pages 2 0 R>>",
        b"<</Type/Pages/Kids[3 0 R]/Count 1>>",
        b"<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>",
    ]

    buf = io.BytesIO()
    buf.write(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(buf.tell())
        buf.write(f"{index} 0 obj".encode() + obj + b"endobj\n")
    xref_offset = buf.tell()
    buf.write(f"xref\n0 {len(objects) + 1}\n".encode())
    buf.write(b"0000000000 65535 f \n")
    for offset in offsets:
        buf.write(f"{offset:010} 00000 n \n".encode())
    buf.write(b"trailer<</Size " + str(len(objects) + 1).encode() + b"/Root 1 0 R>>\n")
    buf.write(b"startxref\n" + str(xref_offset).encode() + b"\n%%EOF")
    return buf.getvalue()


def test_get_extension_returns_lowercase_extension():
    assert document_processing.get_extension("Notes.PDF") == ".pdf"
    assert document_processing.get_extension("chapter1.md") == ".md"


def test_get_extension_returns_empty_string_when_no_dot():
    assert document_processing.get_extension("README") == ""


def test_extract_text_rejects_unsupported_extension():
    text, error = document_processing.extract_text(b"anything", ".docx")
    assert text is None
    assert error == "Unsupported file type"


def test_extract_text_from_valid_pdf_with_content():
    pdf_bytes = _build_pdf_with_text("Hello World")
    text, error = document_processing.extract_text(pdf_bytes, ".pdf")
    assert error is None
    assert text == "Hello World"


def test_extract_text_from_corrupt_pdf_returns_error():
    text, error = document_processing.extract_text(b"not a real pdf file", ".pdf")
    assert text is None
    assert error == "Unable to read this PDF file"


def test_extract_text_from_pdf_with_no_text_returns_error():
    pdf_bytes = _build_blank_pdf()
    text, error = document_processing.extract_text(pdf_bytes, ".pdf")
    assert text is None
    assert error == "No extractable text found in this PDF"


def test_extract_text_from_utf8_plain_text():
    text, error = document_processing.extract_text("Café notes".encode("utf-8"), ".txt")
    assert error is None
    assert text == "Café notes"


def test_extract_text_from_latin1_plain_text_falls_back():
    latin1_only_bytes = "café".encode("latin-1")
    text, error = document_processing.extract_text(latin1_only_bytes, ".md")
    assert error is None
    assert text == "café"


def test_extract_text_from_empty_plain_text_returns_error():
    text, error = document_processing.extract_text(b"   \n\t  ", ".txt")
    assert text is None
    assert error == "This file appears to be empty"