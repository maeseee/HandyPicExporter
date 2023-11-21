#! /usr/bin/python
# TODO read me
import os
import sys
import time
import socket

import FtpUtils

PATH_OF_LAST_BACKUP_FILE = 'DCIM/'  # Do not save it on the root of the phone as it automatically gets deleted
NAME_OF_LAST_BACKUP_FILE = 'LastBackup.txt'
DESTINATION_ROOT_FOLDER = 'C:\\Users\\maese\\Bilder\\FromHandy\\'

ip_address = ""
destination_folder = ""


def __copy_pics(source_directory, destination_sub_folder, last_backup_time, is_favorite):
    destination_directory = destination_folder + destination_sub_folder + "\\"
    print('Copy pictures from ' + source_directory + ' to ' + destination_directory)
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    ftp = FtpUtils.FtpUtils(ip_address)
    ftp.copy_image_files(source_directory, destination_directory, last_backup_time, is_favorite)


def __run_copy_process(last_backup_time):
    __copy_pics('DCIM/MyAlbums/Best', 'Camera', last_backup_time, True)  # Favourites on Oppo
    __copy_pics('MIUI/Gallery/cloud/owner/best', 'Camera', last_backup_time, True)  # Favourites old on Xiaomi
    __copy_pics('Pictures/Gallery/owner/best', 'Camera', last_backup_time, True)  # Favourites on Xiaomi
    __copy_pics('MIUI/Gallery/cloud/owner', 'Camera', last_backup_time, True)  # Albums on Xiaomi
    __copy_pics('DCIM', 'Camera', last_backup_time, False)
    __copy_pics('Pictures', 'Signal', last_backup_time, False)  # Signal on Oppo
    __copy_pics('Bluetooth', 'Bluetooth', last_backup_time, False)  # Bluetooth on Oppo
    __copy_pics('MIUI/ShareMe', 'Bluetooth', last_backup_time, False)  # Bluetooth on Xiaomi
    __copy_pics('Android/media/com.whatsapp/WhatsApp/Media', 'Whatsapp', last_backup_time, False)


def __is_valid_ip(ip):
    try:
        # Check if it's a valid IPv4 or IPv6 address
        socket.inet_pton(socket.AF_INET, ip)  # Try IPv4
        return True
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET6, ip)  # Try IPv6
            return True
        except socket.error:
            return False


def main():
    if not os.path.exists(DESTINATION_ROOT_FOLDER):
        print(f'Destination folder {DESTINATION_ROOT_FOLDER} is not available!')
        sys.exit()

    if not os.listdir(DESTINATION_ROOT_FOLDER):
        print(f'Destination folder {DESTINATION_ROOT_FOLDER} is not empty!')

    print('Have you copied the favourites pictures to the album "Best"? [Yes|No]')
    text = input("")
    if not str(text).lower().startswith("y"):
        sys.exit()

    global ip_address
    ip_address = input("Enter the IP address of the server: ")
    if not __is_valid_ip(ip_address):
        print(f'Invalid ip address {ip_address} entered!')
        sys.exit()

    folder_name = input("Enter the folder name: ")
    global destination_folder
    destination_folder = DESTINATION_ROOT_FOLDER + folder_name + '\\'
    os.makedirs(destination_folder, exist_ok=True)

    ftp = FtpUtils.FtpUtils(ip_address)
    last_backup_timestamp = ftp.read_file_if_available(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE)
    last_backup_timestamp = float(last_backup_timestamp[:-1])
    backup_time_str = time.ctime(last_backup_timestamp)
    print(f'Last backup time was {backup_time_str} from {last_backup_timestamp}')

    __run_copy_process(last_backup_timestamp)

    backup_timestamp = time.time()
    ftp.write_line(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE, str(backup_timestamp))


if __name__ == "__main__":
    main()
