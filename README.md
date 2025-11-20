**Steam Workshop Collection Downloader (SteamCMD-Based)**

This project provides a fully automated Python script that downloads every mod from a Steam Workshop Collection, using SteamCMD efficiently and reliably.

It uses:

    • Batch downloading (multiple mods per SteamCMD session)
    
    • Automatic retries for failed downloads
    
    • Skipping already-downloaded mods
    
    • Automatic movement of downloaded files to your chosen directory
    
    • A progress display (X / Y mods)
    
    • Logging + cleanup
    
    • A final "permanently failed" list
    
    
This tool is designed for mod-heavy games like Transport Fever 2, Rimworld, Cities Skylines, FS22, and others.


**Features**

**Batch downloads**

Reduces SteamCMD reconnect overhead dramatically.

**Retry system**

Failed mods are retried up to 5 times with exponential backoff.

**Skip already downloaded mods**

Useful when updating or syncing collections.

**Automatic folder organization**

Downloaded Workshop items are moved into your final mod directory of your choosing.:

**Progress bar**

Clear: X / Y mods downloaded.

**Failed mod logging**

A failed_mods.txt file is generated at the end.

**Requirements**

    • Windows 10 / 11
    • Python 3.10+
    • SteamCMD installed

**Installing SteamCMD**

Download SteamCMD from Valve:

https://developer.valvesoftware.com/wiki/SteamCMD

Extract it to any folder, for example:

C:\ModDownloader\steamcmd\

Inside this folder you must have:

steamcmd.exe

**Configuring the Script**

At the top of the script you will find:

STEAMCMD_PATH = r"C:\ModDownloader\steamcmd.exe"

Make sure this path points to your actual steamcmd.exe.

Example:

If your SteamCMD is here:

C:\Tools\SteamCMD\steamcmd.exe

Then change the script to:

STEAMCMD_PATH = r"C:\Tools\SteamCMD\steamcmd.exe"


**Usage**

Open a terminal (CMD or PowerShell) inside your project folder:

Then run:

python download_collection.py 1000000 2222222222 anonymous C:\Users\Documents\mods

Where:

    • 1000000 → Game APPID its in the url of the main game page
    
    • 2222222222 → Workshop collection ID its in the url of the collection page
    
    • anonymous → Anonymous Steam login (no account required)
    
    • C:\Users\Documents\mods→ Folder you want to download the mods 
    

**How It Works**

Reads the Workshop collection

Uses Steam Web API to get all mod IDs.

Filters already downloaded mods

If a mod’s folder already exists, it’s skipped.

Downloads in Batches

The script may download 10+ mods in one SteamCMD session for speed.

Moves downloaded mods

Once SteamCMD finishes, the script moves mod folders to your final destination.

Retries failures

Failed mods are retried up to 5 times, individually.

Generates a report

At the end:

    • Progress summary
    
    • List of permanently failed mods
    
    • failed_mods.txt file
    

**Known Issues & Limitations**

SteamCMD can sometimes fail to download certain mods.

**Important notes:**

Some mods cannot be downloaded in batches

SteamCMD sometimes responds with:

    • (Failure)
    
    • (Timeout)
    
    • (No Connection)
    
These failures usually happen because:

    • The mod was deleted or hidden
    
    • The mod is corrupted on Steam servers
    
    • The mod disables anonymous downloading
    
    • Steam rate-limits the Workshop for large collections
    
Even individual downloads may fail

Even with:

steamcmd.exe +login anonymous +workshop_download_item <APPID> <MODID> +quit

Some mods will not download at all, regardless of retries.

This is a Steam-side limitation.


**Disclaimer**

This tool cannot guarantee 100% success for every mod.

Some Workshop items will not download, due to factors outside the script’s control:


    • The item may be private
    
    • The author may have restricted access
    
    • SteamCMD may refuse anonymous download
    
    • The mod may be broken on Steam servers
    
    • Batch downloading introduces extra failure cases
    
If a mod appears in failed_mods.txt, you should:

 Try downloading it manually using SteamCMD:
 
steamcmd.exe +login anonymous +workshop_download_item <APPID> <MODID> +quit

But even manual attempts may fail—this is normal.

 **Optional Improvements (Pull Requests Welcome)**
 
    • Parallelized SteamCMD invocation
    
    • Automatic Steam account login (non-anonymous)
    
    • UI or progress dashboard
    
    • Multi-collection merging
    
    • JSON config file for settings

