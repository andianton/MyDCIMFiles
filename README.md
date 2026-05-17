# MyDCIMFiles
=============

A lightweight, Python-based GUI utility specifically designed for transferring photos and videos between Android devices and FreeBSD via MTP.


## Overview
===========

Transferring media from Android to FreeBSD can be challenging due to MTP protocol quirks. While `aft-mtp-cli` is the reliable backbone for this on BSD, it can be tedious to use manually. **MyDCIMFiles** provides a simple, user-friendly interface to automate this process, making it a dedicated "bridge" for your camera files.


## Prerequisites & Installation
==========================

To run this utility on FreeBSD, you need to install the following dependencies. Open your terminal and run:

[bash]
$ su -
# pkg install python3 android-file-transfer py311-qt6

    Note: If you are using a different Python version, adjust the PyQt6 package name accordingly (e.g., py39-qt6 or py310-qt6).


[Key Features]
    - Automated DCIM Scanning: Instantly lists content from the DCIM/Camera directory of your connected device.
    - Smart Filtering: Quickly search by filename or filter the list by type (Images vs. Videos).
    - Safe Download Workflow: Download files to your local machine with the ability to rename them. The log confirms the final saved name.
    - Secure Uploads: Send files from your PC to the phone's camera folder with built-in Overwrite Protection (Yes/No prompts).
    - Responsive UI: The interface locks during active transfers to prevent accidental clicks and provides real-time status updates.
    - Minimalist Logging: Clean and professional console feedback (e.g., Log: Saved as vacation_2024.jpg -> OK).
    - FreeBSD Optimized: Includes fixes for DBus/Theme warnings by forcing standard Qt platform themes.

[Usage]
    Connect your device: Plug in your phone via USB and set the USB mode to "File Transfer" (MTP).

    Launch the application:
    [bash]
    $ python my_dcim_files.py


[Manage Files]
   - Click **Refresh** to populate the list.
   - Use **Download Selected** to copy files to your PC.
   - Use **Upload to Camera** to move files to your phone.


## Why not a Delete button?
========================

Following the UNIX philosophy of "Do one thing and do it well," this tool is designed strictly as a transfer utility. To prevent accidental data loss (as MTP does not have a Recycle Bin), the delete function was intentionally omitted, keeping your memories safe.


## License
==========
This project is licensed under the **2-Clause BSD License** (the FreeBSD License). It is highly permissive and encourages community use and modification. See the `LICENSE` file for the full text.


