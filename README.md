# Portable installer for portable apps

This Python script allows copying a game folder to another available disk with sufficient space, offering the option to choose between SSD or HDD. Additionally, it creates a desktop shortcut to the executable file inside the copied folder.

## Features

- Detects available disks and displays their free space.
- Allows choosing between SSD, HDD, or manually selecting the destination disk.
- Copies the selected folder to the new location.
- Creates a desktop shortcut for easy game execution.
- Logs all actions in a `log.txt` file.

## Requirements

- Python 3.x
- Required modules: `os`, `shutil`, `psutil`, `winshell`, `win32com.client`, `difflib`, `subprocess`

You can install them by running:

```sh
pip install psutil winshell pywin32
```

## Installation and Usage

1. Clone this repository or download the script.
2. Run the script with Python:
   ```sh
   python script.py
   ```
3. Follow the on-screen instructions to select the copy destination.

## How It Works

1. The script detects the size of the source folder and available disks.
2. It asks for your preferred disk type (SSD, HDD, or manual selection).
3. Allows changing the destination location and folder name.
4. Copies the folder to the new location.
5. Searches for `.exe` files inside the folder and creates a desktop shortcut.

## Activity Log

All actions performed by the script are saved in `log.txt` for reference and debugging.

## Notes

- If no disks with sufficient space are detected, the script will prompt for manual input.
- If multiple `.exe` files are found in the folder, it will allow selecting one for shortcut creation.

## License

This project is licensed under the GNU GENERAL PUBLIC LICENSE. Feel free to use and modify it!

