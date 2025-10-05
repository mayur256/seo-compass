"""Storage utilities for file generation and ZIP creation."""

import csv
import io
import json
import zipfile
from typing import Dict, List


def make_csv_from_dicts(rows: List[dict], headers: List[str]) -> bytes:
    """Create CSV bytes from list of dictionaries."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode('utf-8')


def write_text_file(content: str) -> bytes:
    """Convert text content to bytes."""
    return content.encode('utf-8')


def write_json_file(data: dict) -> bytes:
    """Convert dictionary to JSON bytes."""
    return json.dumps(data, indent=2, default=str).encode('utf-8')


def make_zip(files: Dict[str, bytes]) -> bytes:
    """Create ZIP file from dictionary of filename -> content bytes."""
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in files.items():
            zip_file.writestr(filename, content)
    
    zip_buffer.seek(0)
    return zip_buffer.getvalue()