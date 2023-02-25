#!/usr/bin/env python3

import os
import subprocess
import threading
import tkinter as tk
import configparser
import logging
import tkinter.ttk as ttk


class DataSyncApp:
    def __init__(self, master):
        # Save the master widget reference
        self.master = master

        # Set the title and size of the main window
        master.title("Data Sync")
        master.geometry("800x645")
        master.configure(background="gray")

        # Add a label to the main window
        self.label = tk.Label(
            master, text="Sync data from local to remote machine", background="gray"
        )
        self.label.pack()

        # Add a frame to the main window
        self.frame = tk.Frame(master)
        self.frame.pack(pady=10)

        # Add a scrollbar to the frame
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Add a text box to the frame
        self.output_box = tk.Text(
            self.frame, yscrollcommand=self.scrollbar.set, background="white", wrap=tk.WORD
        )
        self.output_box.pack(expand=True, fill=tk.BOTH)

        # Connect the scrollbar to the text box
        self.scrollbar.config(command=self.output_box.yview)

        # Add a clear button to the main window
        self.clear_button = tk.Button(
            master, text="Clear", command=self.clear_text, background="blue", foreground="white"
        )
        self.clear_button.pack()

        # Add a verbose checkbox to the main window
        self.verbose_var = tk.BooleanVar()
        self.verbose_checkbox = tk.Checkbutton(
            master, text="Verbose", variable=self.verbose_var, onvalue=True, offvalue=False
        )
        self.verbose_checkbox.pack()

        # Add a sync button to the main window
        self.sync_button = tk.Button(
            master, text="Sync", command=self.run_sync, background="blue", foreground="white"
        )
        self.sync_button.pack()

        # Add a quit button to the main window
        self.quit_button = tk.Button(
            master, text="Quit", command=master.quit, background="red", foreground="white"
        )
        self.quit_button.pack(pady=10)

        # Initialize the progress bar to None
        self.progress_bar = None

        # Initialize the number of files to sync and synced
        self.num_files_to_sync = 0
        self.num_files_synced = 0

        # Read the config file
        self.config = configparser.ConfigParser()
        self.config.read("dataSync.ini")

        # Initialize the logger
        self.logger = logging.getLogger("DataSync")
        self.logger.setLevel(logging.ERROR)
        handler = logging.FileHandler("dataSync.log")
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    # Method to clear the text in the output box
    def clear_text(self):
        self.output_box.delete("1.0", tk.END)

    # Method to update the status message
    def update_status(self, message):
        self.output_box.insert(tk.END, message + "\n")

    # Method to update the list of synced files
    def update_file_list(self, file_name):
        self.output_box.insert(tk.END, file_name + "\n")
        self.output_box.see(tk.END)
        self.num_files_synced += 1
        if self.progress_bar is not None:
            self.progress_bar["value"] = self.num_files_synced

    # Method to generate the rsync options
    @staticmethod
    def get_rsync_options(source_dir, destination_dir, ssh_key, verbose):
        rsync_options = ["rsync", "-az", "-e", f"ssh -i {ssh_key}", source_dir, destination_dir]
        if verbose:
            rsync_options.insert(2, "-v")
        return rsync_options

    # Method to sync the data
    def sync_data(self, source_dir, destination_dir, ssh_key, verbose):
        # Check if the source directory exists
        if not os.path.isdir(source_dir):
            self.update_status(f"Error: source directory {source_dir} does not exist.")
            return

        # Check if the ssh key file exists
        if not os.path.isfile(ssh_key):
            self.update_status(f"Error: ssh key file {ssh_key} does not exist.")
            return

        # Generate the rsync options
        rsync_options = self.get_rsync_options(source_dir, destination_dir, ssh_key, verbose)

        # Count the number of files to sync
        process = subprocess.Popen(rsync_options + ["--dry-run"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.num_files_to_sync = len(process.stdout.readlines())
        process.wait()
        self.num_files_synced = 0

        # Create the progress bar if there are files to sync
        self.progress_bar = tk.ttk.Progressbar(
            self.master, orient="horizontal", length=200, mode="determinate"
        )
        self.progress_bar.pack()
        self.progress_bar["maximum"] = self.num_files_to_sync
        self.progress_bar["value"] = 0

        # Run the rsync command to sync the data from local to remote

        process = subprocess.Popen(rsync_options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            self.update_file_list(line.decode("utf-8").strip())
        process.wait()

        # Check if the sync from local to remote was successful
        if process.returncode == 0:
            self.update_status("Data synced successfully from local to remote.")
        else:
            error_message = str(process.stderr.read().decode("utf-8").strip())
            self.update_status(f"Sync from local to remote failed: {error_message}")
            self.logger.error(f"Sync from local to remote failed: {error_message}")

        # Swap the source and destination directories for the next sync
        source_dir = self.config.get("DataSync", "destination_dir")
        destination_dir = self.config.get("DataSync", "source_dir")
        rsync_options = self.get_rsync_options(source_dir, destination_dir, ssh_key, verbose)

        # Create the progress bar if there are files to sync
        if self.num_files_to_sync > 0:
            self.progress_bar["maximum"] = self.num_files_to_sync
            self.progress_bar["value"] = 0
            self.num_files_synced = 0

        # Run the rsync command to sync the data from remote to local
        process = subprocess.Popen(rsync_options, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in iter(process.stdout.readline, b''):
            self.update_file_list(line.decode("utf-8").strip())
        process.wait()

        # Check if the sync from remote to local was successful
        if process.returncode == 0:
            self.update_status("Data synced successfully from remote to local.")
        else:
            error_message = str(process.stderr.read().decode("utf-8").strip())
            self.update_status(f"Sync from remote to local failed: {error_message}")
            self.logger.error(f"Sync from remote to local failed: {error_message}")

        # Destroy the progress bar
        if self.progress_bar is not None:
            self.progress_bar.destroy()
            self.progress_bar = None

    def run_sync(self):
        # Get the source and destination directories, the ssh key, and the verbose setting from the config
        source_dir = self.config.get("DataSync", "source_dir")
        destination_dir = self.config.get("DataSync", "destination_dir")
        ssh_key = self.config.get("DataSync", "ssh_key")
        verbose = self.verbose_var.get()

        # Start the sync in a new thread
        sync_thread = threading.Thread(target=self.sync_data, args=(source_dir, destination_dir, ssh_key, verbose))
        sync_thread.start()


# Main function to run the program
if __name__ == "__main__":
    # Initialize the logger
    logging.basicConfig(filename="dataSync.log", level=logging.ERROR)
    root = tk.Tk()
    app = DataSyncApp(root)
    root.mainloop()
