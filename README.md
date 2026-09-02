# USBootable

A Windows utility for preparing and working with bootable USB drives.

## Overview

**USBootable** is a Windows-focused utility designed to simplify common tasks involved in creating and managing bootable USB media.

The project is organized into separate source, configuration, and tooling directories to keep the application maintainable and easy to build.

## Project Structure

```text
USBootable/
├── config/          # Application configuration
├── src/             # Main application source code
├── tools/           # Development and utility scripts
├── cli.spec         # PyInstaller build specification
├── README.md        # Project documentation
└── .gitignore       # Git ignore rules
```
## Requirements

- Windows
- Python 3.x
- A working Python virtual environment is recommended
  
Depending on the functionality being used, the application may require administrator privileges when interacting with disks or USB devices.

## Installation
Clone the repository:

```
git clone <repository-url>
cd "USBootable"
```

Create and activate a virtual environment:

```
python -m venv .venv
.venv\Scripts\activate
```

Install the project's dependencies if a dependency file is provided:

`pip install -r requirements.txt`

If the project does not currently include a `requirements.txt`, install the required packages used by the source code before running the application.

## Running from Source
Run the appropriate entry point from the `src` directory.

For example:

```
python src/cli.py
```

## Building
The project includes a PyInstaller specification:

`cli.spec`

If PyInstaller is installed, the application can be built with:

`pyinstaller cli.spec`

Build output is generated in the `build/` and `dist/` directories.

These generated directories are intentionally excluded from version control.

## Safety
USB and disk-related operations can potentially result in data loss if the wrong device is selected.

Before performing any operation that writes to or modifies a disk:

Verify the selected USB/device.
Back up any important data.
Do not disconnect a device while an operation is in progress.
Run the application with administrator privileges when required.
Double-check destructive operations before confirming them.
The user is responsible for selecting the correct storage device and protecting their data.

## Development
The repository is structured so that generated files and local development environments remain outside version control.

The following directories are intentionally ignored:

```
.idea/
.venv/
__pycache__/
build/
dist/
```

## License
No license has currently been specified for this project.

## Status
Version: 1.1

This project is under active development.
