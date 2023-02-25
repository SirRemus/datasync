# Data Sync

A GUI application for data synchronization between a local machine and a remote machine using `rsync` and `Tkinter`.

## Requirements

- Python 3
- Tkinter (Python's built-in GUI framework)
- `rsync` command

## Usage

1. Clone or download the repository.
2. Make sure the `rsync` command is installed on your machine.
3. Edit the `dataSync.ini` file to specify the source directory, destination directory, and ssh key.
4. Run the `datasync.py` script:

    ```bash
    python3 datasync.py
    ```

5. The GUI will appear. Use the checkbox to turn on verbose mode if desired.
6. Click the "Sync" button to start the synchronization.
7. The status of the sync will be displayed in the text box and the progress bar will show the progress.
8. The log file `dataSync.log` will be updated with any errors.

## Contributing

If you find any bugs or have any suggestions for improvements, please open an issue or create a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
