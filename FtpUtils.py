from datetime import datetime
import ftplib
import io
import os
from ftplib import FTP

import ImageUtils


class FtpUtils:

    def __init__(self, ftp_server):
        ftp_user = "android"
        ftp_pass = "mySweetHandyAccess"
        ftp_port = 2221

        self.ftp = FTP()
        self.ftp.connect(ftp_server, ftp_port)
        self.ftp.login(ftp_user, ftp_pass)

    def __del__(self):
        self.ftp.quit()

    def read_modification_date(self, full_filename):
        mod_time = self.ftp.sendcmd("MDTM " + full_filename)[4:]
        return mod_time

    def write_line(self, file_path, text):
        stream = io.BytesIO(text.encode())
        self.ftp.storbinary(f"STOR {file_path}", stream)
        stream.close()

    def read_file_if_available(self, file_path):
        content = ""

        def callback(line):
            nonlocal content
            content += line + "\n"

        try:
            self.ftp.retrlines(f"RETR {file_path}", callback)
        except ftplib.error_perm:
            return "0\n"

        return content

    def __exit_directory(self, number_subdirectories):
        for i in range(number_subdirectories):
            self.ftp.cwd("..")

    def __directory_exists(self, directory):
        try:
            self.ftp.cwd(directory)
            number_subdirectories = directory.count('/') + 1
            self.__exit_directory(number_subdirectories)
            return True
        except ftplib.error_perm as e:
            if str(e).startswith("550"):
                return False
            else:
                raise

    def __get_file_modification_time(self, filename):
        modification_time_str = self.ftp.sendcmd('MDTM ' + filename)[4:]
        modification_time = int(float(modification_time_str))
        modification_date_time = datetime.strptime(str(modification_time), '%Y%m%d%H%M%S')
        # convert the datetime object to an integer representing the number of seconds since 1970
        modification_timestamp = int(modification_date_time.timestamp())
        return modification_timestamp

    def __get_file_list_of_current_directory(self):
        file_list = []
        try:
            file_list = self.ftp.nlst()
            print(file_list)
        except ftplib.error_perm as resp:
            if str(resp) == "550 No files found":
                print("No files in this directory")
            else:
                raise
        return file_list

    def __copy_subfolder(self, source_folder, destination_directory, last_backup_timestamp, is_favorite):
        self.ftp.cwd(source_folder)
        self.ftp.sendcmd('TYPE I')

        file_list = self.__get_file_list_of_current_directory()

        number_of_elements = len(file_list)
        number_elements_processed = 0
        for filename in file_list:
            number_elements_processed = number_elements_processed + 1
            print("\rProcess " + str(number_elements_processed) + "/" + str(number_of_elements), end='', flush=True)

            if ImageUtils.is_in_ignore_list(filename):
                continue

            if self.__directory_exists(filename):
                print("copy subdirectory " + filename)
                self.__copy_subfolder(filename, destination_directory, last_backup_timestamp, is_favorite)
                continue

            if not ImageUtils.has_image_file_ending(filename):
                print("File " + filename + " has been ignored!")
                continue

            file_path = destination_directory + filename
            if os.path.exists(file_path):
                continue

            modification_timestamp = self.__get_file_modification_time(filename)
            if modification_timestamp < last_backup_timestamp:
                continue

            with open(file_path, "wb") as f:
                self.ftp.retrbinary("RETR " + filename, f.write)

            if is_favorite:
                ImageUtils.five_stars_to_file(file_path)

        self.__exit_directory(1)

    def copy_image_files(self, source_directory, destination_directory, last_backup_timestamp, is_favorite):
        source_directory_exists = self.__directory_exists(source_directory)
        if not source_directory_exists:
            print("Directory " + source_directory + " does not exist")
            return

        self.__copy_subfolder(source_directory, destination_directory, last_backup_timestamp, is_favorite)
