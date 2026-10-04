"""
voucher_pdf.py: reads the voucher that Accounting > Voucher Search > Preview
opens as a PDF, and turns it into plain values a test can compare.

The Preview is a PDF viewer in a new browser tab, so the page itself has no
text. The test fetches the same address with the logged-in session and gives
the bytes to `read_voucher_text`. The text is read in "layout" mode, which
keeps the table columns apart.
"""
import io
import re

from pypdf import PdfReader

AMOUNT = r"[\d,]+\.\d{2}"
# one table line: Accounts Code, Heads of Accounts, Debit, Credit
LINE_PATTERN = re.compile(rf"^\s*(\d{{10}}-\d{{2}})\s+(.+?)\s{{2,}}({AMOUNT})\s+({AMOUNT})", re.MULTILINE)
TOTALS_PATTERN = re.compile(rf"Amount \(In Word\)\s*:\s*(.+?)\s{{2,}}({AMOUNT})\s+({AMOUNT})")


def read_voucher_text(pdf_bytes: bytes) -> str:
    """Return the text of the first page of the voucher PDF, columns kept apart."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return reader.pages[0].extract_text(extraction_mode="layout")


def parse_voucher(text: str) -> dict:
    """
    Pick the values a test checks out of the voucher text:
        title, branch, project, voucher_number (VIN), creation_date,
        posted_date, lines [{account_code, head, debit, credit}],
        amount_in_words, total_debit, total_credit, reference_numbers.
    A value that is not found is None (or an empty list).
    """
    def first(pattern, flags=0):
        match = re.search(pattern, text, flags)
        return match.group(1).strip() if match else None

    totals = TOTALS_PATTERN.search(text)
    return {
        "title": first(r"(JOURNAL VOUCHER|CREDIT VOUCHER|DEBIT VOUCHER|TRANSFER VOUCHER)"),
        "branch": first(r"(\[[A-Z]{2} - [A-Z0-9]+\][^\n]*)"),
        "project": first(r"Project:\s*([^\n]+)"),
        "voucher_number": first(r"VIN:\s*(\d+)"),
        "creation_date": first(r"Creation Date\s*:\s*(\d{2}/\d{2}/\d{4})"),
        "posted_date": first(r"Posted Date\s*:\s*(\d{2}/\d{2}/\d{4})"),
        "lines": [
            {"account_code": code, "head": head.strip(), "debit": debit, "credit": credit}
            for code, head, debit, credit in LINE_PATTERN.findall(text)
        ],
        "amount_in_words": totals.group(1).strip() if totals else None,
        "total_debit": totals.group(2) if totals else None,
        "total_credit": totals.group(3) if totals else None,
        "reference_numbers": re.findall(r"BBDEXP\d+", text),
    }
