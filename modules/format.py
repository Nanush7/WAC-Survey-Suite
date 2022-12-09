"""
Fix CSV format
"""
import pandas

from re import sub


def fix_token_columns(df: pandas.DataFrame) -> pandas.DataFrame:
    """
    Move tokens to the correct column
    and delete bad_token_column from dataframe.
    """
    bad_token_column = df.columns[-1]
    # ...
    df.drop([bad_token_column], axis=1)
    return df


def fix_headers(file_path: str) -> None:
    """
    Remove "Unnamed: [int]" from column headers.
    """
    with open(file_path, 'r') as f:
        content = f.read()

    content = sub(r'(Unnamed: )[0-9]+', '', content)

    # Write fixed content.
    with open(file_path, 'w') as f:
        f.write(content)
