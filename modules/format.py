"""
Fix CSV format
"""
import pandas

from re import sub

WCA_TOKEN_FIELD = 'wca_token'


def fix_headers(file_path: str) -> None:
    """
    Remove "Unnamed: ..." from column headers.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    content = sub(r'(Unnamed: )[0-9]+', '', content)

    # Write fixed content.
    with open(file_path, 'w') as f:
        f.write(content)
