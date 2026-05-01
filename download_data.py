"""
Download all raw data for the respiratory disease prediction pipeline.

EPA AQS files are downloaded as zips and extracted.
CDC NSSP file is downloaded via the Socrata CSV API.
All 21 files are downloaded in parallel.

Usage:
    python download_data.py           # download everything
    python download_data.py --dry-run # print what would be downloaded
"""

import argparse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).parent

# --- EPA AQS ---

EPA_FILES = [
    # (dest_subfolder, url)
    ("pm25",        "https://aqs.epa.gov/aqsweb/airdata/daily_88101_2025.zip"),
    ("pm25",        "https://aqs.epa.gov/aqsweb/airdata/daily_88101_2024.zip"),
    ("pm25",        "https://aqs.epa.gov/aqsweb/airdata/daily_88101_2023.zip"),
    ("pm25",        "https://aqs.epa.gov/aqsweb/airdata/daily_88101_2022.zip"),

    ("no2",         "https://aqs.epa.gov/aqsweb/airdata/daily_42602_2025.zip"),
    ("no2",         "https://aqs.epa.gov/aqsweb/airdata/daily_42602_2024.zip"),
    ("no2",         "https://aqs.epa.gov/aqsweb/airdata/daily_42602_2023.zip"),
    ("no2",         "https://aqs.epa.gov/aqsweb/airdata/daily_42602_2022.zip"),

    ("ozone",       "https://aqs.epa.gov/aqsweb/airdata/daily_44201_2025.zip"),
    ("ozone",       "https://aqs.epa.gov/aqsweb/airdata/daily_44201_2024.zip"),
    ("ozone",       "https://aqs.epa.gov/aqsweb/airdata/daily_44201_2023.zip"),
    ("ozone",       "https://aqs.epa.gov/aqsweb/airdata/daily_44201_2022.zip"),

    ("temperature", "https://aqs.epa.gov/aqsweb/airdata/daily_TEMP_2025.zip"),
    ("temperature", "https://aqs.epa.gov/aqsweb/airdata/daily_TEMP_2024.zip"),
    ("temperature", "https://aqs.epa.gov/aqsweb/airdata/daily_TEMP_2023.zip"),
    ("temperature", "https://aqs.epa.gov/aqsweb/airdata/daily_TEMP_2022.zip"),

    ("humidity",    "https://aqs.epa.gov/aqsweb/airdata/daily_RH_DP_2025.zip"),
    ("humidity",    "https://aqs.epa.gov/aqsweb/airdata/daily_RH_DP_2024.zip"),
    ("humidity",    "https://aqs.epa.gov/aqsweb/airdata/daily_RH_DP_2023.zip"),
    ("humidity",    "https://aqs.epa.gov/aqsweb/airdata/daily_RH_DP_2022.zip"),
]

# --- CDC NSSP ---

CDC_URL       = "https://data.cdc.gov/api/v3/views/vjzj-u7u8/query.csv"
CDC_APP_TOKEN = "nmedEEGsEBzcqD5CLxHrcVtHL"
CDC_DEST      = ROOT / "data" / "raw" / "respiratory" / "nssp_respiratory.csv"


def fetch_epa_file(subfolder: str, url: str) -> str:
    dest_dir = ROOT / "data" / "raw" / subfolder
    dest_dir.mkdir(parents=True, exist_ok=True)

    zip_name = url.split("/")[-1]
    csv_name = zip_name.replace(".zip", ".csv")
    csv_path = dest_dir / csv_name

    if csv_path.exists():
        return f"skip  {csv_path.relative_to(ROOT)}"

    zip_path = dest_dir / zip_name
    urllib.request.urlretrieve(url, zip_path)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(dest_dir)
    zip_path.unlink()

    # Some EPA zips nest the CSV in a subdirectory — flatten if needed
    if not csv_path.exists():
        nested = next(dest_dir.rglob(csv_name), None)
        if nested:
            nested.rename(csv_path)
            try:
                nested.parent.rmdir()
            except OSError:
                pass

    return f"done  {csv_path.relative_to(ROOT)}"


def fetch_cdc_file() -> str:
    if CDC_DEST.exists():
        return f"skip  {CDC_DEST.relative_to(ROOT)}"

    CDC_DEST.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(CDC_URL, headers={"X-App-Token": CDC_APP_TOKEN})
    with urllib.request.urlopen(req) as resp, open(CDC_DEST, "wb") as out:
        out.write(resp.read())
    return f"done  {CDC_DEST.relative_to(ROOT)}"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Print what would be downloaded without downloading")
    args = parser.parse_args()

    if args.dry_run:
        print("Dry run — no files will be downloaded.\n")
        for subfolder, url in EPA_FILES:
            csv_name = url.split("/")[-1].replace(".zip", ".csv")
            print(f"  {url}  ->  data/raw/{subfolder}/{csv_name}")
        print(f"  {CDC_URL}  ->  {CDC_DEST.relative_to(ROOT)}")
        return

    # Build task list: all EPA files + CDC file
    tasks = [(subfolder, url) for subfolder, url in EPA_FILES]

    print(f"Downloading {len(tasks) + 1} files in parallel ...\n")

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(fetch_epa_file, sf, url): url for sf, url in tasks}
        futures[pool.submit(fetch_cdc_file)] = CDC_URL

        for future in as_completed(futures):
            url = futures[future]
            try:
                print(f"  {future.result()}")
            except Exception as e:
                print(f"  FAILED  {url}  ({e})")

    print("\nAll done. Run:  make all")


if __name__ == "__main__":
    main()
