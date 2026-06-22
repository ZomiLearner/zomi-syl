import pandas as pd
import re
import requests
from io import StringIO

def read_google_sheet(direct_url, sheet_name=None):
    """
    Read a publicly shared Google Sheet from its direct URL.

    Parameters:
        direct_url (str): Full Google Sheets URL
        sheet_name (str, optional): Name of specific sheet tab (overrides gid)

    Returns:
        pandas.DataFrame or None
    """

    try:
        # Extract sheet_id
        sheet_id_match = re.search(r'/d/([a-zA-Z0-9_-]+)', direct_url)
        if not sheet_id_match:
            print("Error: Could not extract sheet_id from URL")
            return None

        sheet_id = sheet_id_match.group(1)
        print(f"✓ Extracted sheet_id: {sheet_id}")

        # Extract gid if sheet_name not provided
        gid = None
        if not sheet_name:
            gid_match = re.search(r'[#&]gid=(\d+)', direct_url)
            if gid_match:
                gid = gid_match.group(1)
                print(f"✓ Extracted gid: {gid}")

        # Construct export URL
        if sheet_name:
            url = (
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?"
                f"tqx=out:csv&sheet={sheet_name}"
            )
            print(f"📄 Using sheet name: '{sheet_name}'")
        elif gid:
            url = (
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?"
                f"format=csv&gid={gid}"
            )
            print(f"📄 Using gid: {gid}")
        else:
            url = (
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?"
                f"format=csv"
            )
            print("📄 Using first sheet")

        print("🔄 Fetching data...")

        # Fetch CSV manually
        resp = requests.get(url)
        resp.raise_for_status()  # triggers RequestException on HTTP errors

        # Load into pandas
        df = pd.read_csv(StringIO(resp.text))

        print(f"✓ Success! Loaded {len(df):,} rows and {len(df.columns)} columns")
        return df

    except requests.exceptions.RequestException as e:
        print(f"✗ Network or HTTP error: {e}")
        print("  Check if the sheet is publicly shared and the URL is correct.")
    except pd.errors.EmptyDataError:
        print("✗ The sheet appears to be empty")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

    return None


if __name__ == "__main__":
    print("This module provides read_google_sheet(). Import it from other scripts.")
