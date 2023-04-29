from datetime import datetime
import ftplib
import io
import os
from ftplib import FTP

import ImageUtils


def open_ftp_connection():
    ftp_server = "192.168.50.211"
    ftp_user = "android"
    ftp_pass = "mySweetHandyAccess"
    ftp_port = 2221

    ftp = FTP()
    ftp.connect(ftp_server, ftp_port)
    ftp.login(ftp_user, ftp_pass)

    return ftp


def close_ftp_connection(ftp):
    ftp.quit()


def read_modification_date(full_filename):
    ftp = open_ftp_connection()

    mod_time = ftp.sendcmd("MDTM " + full_filename)[4:]

    close_ftp_connection(ftp)
    return mod_time


def read_first_line(full_file_name):
    ftp = open_ftp_connection()

    with io.StringIO() as file_obj:
        ftp.retrlines('RETR ' + full_file_name, file_obj.write)
        file_contents = file_obj.getvalue()

    close_ftp_connection(ftp)
    return float(file_contents)


def write_line(backup_file_path, text):
    ftp = open_ftp_connection()

    with open(text, 'rb') as f:
        # Use the STOR command to upload the file to the remote server
        ftp.cwd(backup_file_path)
        ftp.storbinary(f'STOR {backup_file_path}', f)

    close_ftp_connection(ftp)


def is_file_available(directory, filename):
    ftp = open_ftp_connection()

    ftp.cwd(directory)
    file_list = ftp.nlst()
    file_available = filename in file_list

    close_ftp_connection(ftp)
    return file_available


def create_file(directory, filename):
    ftp = open_ftp_connection()

    ftp.cwd(directory)
    with open(filename, 'w') as file:
        file.write('0')

    close_ftp_connection(ftp)


def __exit_directory(ftp, number_subdirectories):
    for i in range(number_subdirectories):
        ftp.cwd("..")


def __directory_exists(ftp, directory):
    try:
        ftp.cwd(directory)
        number_subdirectories = directory.count('/') + 1
        __exit_directory(ftp, number_subdirectories)
        return True
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            return False
        else:
            raise


def __has_image_file_ending(filename):
    return filename.endswith('.jpg') or \
        filename.endswith('.jpeg') or \
        filename.endswith('.png') or \
        filename.endswith('.giv') or \
        filename.endswith('.mp4')


def __get_file_modification_time(ftp, filename):
    modification_time_str = ftp.sendcmd('MDTM ' + filename)[4:]
    modification_time = int(float(modification_time_str))
    modification_date_time = datetime.strptime(str(modification_time), '%Y%m%d%H%M%S')
    # convert the datetime object to an integer representing the number of seconds since 1970
    modification_timestamp = int(modification_date_time.timestamp())
    return modification_timestamp


def __copy_subfolder(ftp, source_folder, destination_directory, last_backup_timestamp, is_favorite):
    ftp.cwd(source_folder)
    ftp.sendcmd('TYPE I')

    file_list = []
    try:
        file_list = ftp.nlst()
        print(file_list)
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print("No files in this directory")
        else:
            raise

    number_of_elements = len(file_list)
    number_elements_processed = 0
    for filename in file_list:
        number_elements_processed = number_elements_processed + 1
        print("\rProcess " + str(number_elements_processed) + "/" + str(number_of_elements), end='', flush=True)
        if __directory_exists(ftp, filename):
            print("copy subdirectory " + filename)
            __copy_subfolder(ftp, filename, destination_directory, last_backup_timestamp, is_favorite)
            continue

        if not __has_image_file_ending(filename):
            print("File " + filename + " has been ignored!")
            continue

        file_path = destination_directory + filename
        if os.path.exists(file_path):
            continue

        modification_timestamp = __get_file_modification_time(ftp, filename)

        if modification_timestamp < last_backup_timestamp:
            continue

        with open(file_path, "wb") as f:
            ftp.retrbinary("RETR " + filename, f.write)

        if is_favorite:
            ImageUtils.five_stars_to_file(file_path)

    __exit_directory(ftp, 1)


def copy_image_files(source_directory, destination_directory, last_backup_timestamp, is_favorite):
    ftp = open_ftp_connection()

    source_directory_exists = __directory_exists(ftp, source_directory)
    if not source_directory_exists:
        print("Directory " + source_directory + " does not exist")
        return

    __copy_subfolder(ftp, source_directory, destination_directory, last_backup_timestamp, is_favorite)

    close_ftp_connection(ftp)
