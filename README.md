# Data Sync

A simple data synchronization application with a GUI built using Python and Tkinter.


## Requirements

- Python 3
- Tkinter (Python's built-in GUI framework)
- `rsync` command

## Usage

1. Clone or download the repository.
2. Configure the datasync.ini file with your source and destination directories, SSH key.
3. Run the script using the following command:

    ```bash
    python3 datasync.py
    ```

The application will start and display the main window. You can then click the "Sync" button to start the synchronization process.

## Features

- source_dir: The local source directory for the data synchronization.
- destination_dir: The remote destination directory for the data synchronization.
- ssh_key: The path to the SSH key for accessing the remote machine.

## Limitations

-  The application assumes that rsync is installed and available in the PATH.
-  The script does not handle authentication for the remote machine, it assumes that the SSH key is properly set up and can be used to access the remote machine without a password.

## License

This project is licensed under the [MIT License](LICENSE).
