import subprocess
import requests
import os
import sys
import time
import shutil

STEAMCMD_PATH = r"C:\ModDownloader\steamcmd.exe"  # Path to steamcmd.exe
BATCH_SIZE = 50               # Default batch size
BATCH_DELAY = 2               # Seconds between batches
MAX_RETRIES = 5               # Increased retries for reliability
RETRY_DELAY = 5               # Base delay for retries

final_outdir = ""             # will be set from command-line


def get_collection_items(collection_id):
    url = "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
    data = {"collectioncount": 1, "publishedfileids[0]": str(collection_id)}

    try:
        resp = requests.post(url, data=data, timeout=15)
        resp.raise_for_status()
        parsed = resp.json()
        children = parsed["response"]["collectiondetails"][0].get("children", [])
        return [c["publishedfileid"] for c in children]
    except Exception as e:
        print(f"[ERROR] Could not fetch collection: {e}")
        return []


def filter_already_downloaded(item_ids, final_outdir):
    filtered = []
    for item_id in item_ids:
        path = os.path.join(final_outdir, str(item_id))
        if not os.path.isdir(path) or not os.listdir(path):
            filtered.append(item_id)
        else:
            print(f"[INFO] Skipping already downloaded mod {item_id}")
    return filtered


def chunk_list(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def download_batch(appid, item_ids, login, temp_outdir):
    os.makedirs(temp_outdir, exist_ok=True)
    cmd = [STEAMCMD_PATH, "+force_install_dir", os.path.abspath(temp_outdir), "+login", login]

    for item_id in item_ids:
        cmd += ["+workshop_download_item", str(appid), str(item_id)]

    cmd += ["+quit"]

    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] SteamCMD batch failed: {e}")
        return False


def move_downloads(appid, item_ids, temp_outdir, final_outdir):
    workshop_root = os.path.join(temp_outdir, "steamapps", "workshop", "content", str(appid))
    os.makedirs(final_outdir, exist_ok=True)
    successful, failed = [], []

    for item_id in item_ids:
        src = os.path.join(workshop_root, str(item_id))
        dst = os.path.join(final_outdir, str(item_id))
        if os.path.isdir(src) and os.listdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.move(src, dst)
            print(f"[INFO] Moved mod {item_id} to {dst}")
            successful.append(item_id)
        else:
            failed.append(item_id)
    return successful, failed


def retry_failed(appid, failed_ids, login, temp_outdir, downloaded_count, total_mods):
    still_failed = failed_ids.copy()
    for attempt in range(1, MAX_RETRIES + 1):
        if not still_failed:
            break
        print(f"[INFO] Retry attempt {attempt} for {len(still_failed)} mods...")
        next_failed = []
        for item_id in still_failed:
            time.sleep(RETRY_DELAY * attempt)
            print(f"[INFO] Retrying mod {item_id}...")
            download_batch(appid, [item_id], login, temp_outdir)
            _, failed = move_downloads(appid, [item_id], temp_outdir, final_outdir)
            if failed:
                next_failed.extend(failed)
            else:
                downloaded_count += 1
            print(f"[PROGRESS] {downloaded_count}/{total_mods} mods downloaded so far")
        still_failed = next_failed
    return still_failed, downloaded_count


def main():
    global final_outdir

    if len(sys.argv) < 5:
        print("Usage: python download_collection.py <APPID> <COLLECTION_ID> <LOGIN> <FINAL_OUTDIR>")
        sys.exit(1)

    appid = sys.argv[1]
    collection_id = sys.argv[2]
    login = sys.argv[3]
    final_outdir = sys.argv[4]

    temp_outdir = "steamcmd_temp"

    all_items = get_collection_items(collection_id)
    item_ids = filter_already_downloaded(all_items, final_outdir)
    total_mods = len(item_ids)

    if not item_ids:
        print("[INFO] All mods already downloaded. Nothing to do.")
        return

    print(f"[INFO] Found {total_mods} mods to download.")
    downloaded_count = 0
    all_successful, all_failed = [], []

    for i, batch in enumerate(chunk_list(item_ids, BATCH_SIZE), start=1):
        print(f"[INFO] Downloading batch {i}/{(total_mods-1)//BATCH_SIZE+1} ({len(batch)} mods)...")
        download_batch(appid, batch, login, temp_outdir)
        success, failed = move_downloads(appid, batch, temp_outdir, final_outdir)
        all_successful.extend(success)
        all_failed.extend(failed)
        downloaded_count += len(success)
        print(f"[PROGRESS] {downloaded_count}/{total_mods} mods downloaded so far")
        time.sleep(BATCH_DELAY)

    if all_failed:
        print(f"[INFO] Retrying {len(all_failed)} failed mods individually...")
        all_failed, downloaded_count = retry_failed(appid, all_failed, login, temp_outdir, downloaded_count, total_mods)

    print("[DONE] Download complete.")
    print(f"[SUMMARY] Successfully downloaded: {downloaded_count}/{total_mods}")
    if all_failed:
        print(f"[SUMMARY] Permanently failed mods ({len(all_failed)}): {all_failed}")
        with open("failed_mods.txt", "w") as f:
            f.write("\n".join(all_failed))


if __name__ == "__main__":
    main()
