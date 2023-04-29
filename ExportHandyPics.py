#! /usr/bin/python

import os
import sys
import time

import FtpUtils

PATH_OF_LAST_BACKUP_FILE = 'DCIM/'  # Do not save it on the root of the phone as it automatically gets deleted
NAME_OF_LAST_BACKUP_FILE = 'LastBackup.txt'
# DESTINATION_FOLDER = 'C:\\Users\\maese\\Bilder\\FromHandy\\'
DESTINATION_FOLDER = 'C:\\Users\\maese\\Documents\\Temp\\'


def __copy_pics(source_directory, destination_folder, last_backup_time, is_favorite):
    destination_directory = DESTINATION_FOLDER + destination_folder + "\\"
    print('Copy pictures from ' + source_directory + ' to ' + destination_directory)
    if not os.path.exists(destination_directory):
        os.makedirs(destination_directory)

    FtpUtils.copy_image_files(source_directory, destination_directory, last_backup_time, is_favorite)


def __run_copy_process(last_backup_time):
    __copy_pics('DCIM/MyAlbums/Best', 'Camera', last_backup_time, True)  # Favourites on Oppo
    __copy_pics('MIUI/Gallery/cloud/owner/best', 'Camera', last_backup_time, True)  # Favourites on Xiaomi
    __copy_pics('MIUI/Gallery/cloud/owner', 'Camera', last_backup_time, True)  # Albums on Xiaomi
    __copy_pics('DCIM', 'Camera', last_backup_time, False)
    __copy_pics('Pictures', 'Signal', last_backup_time, False)  # Signal on Oppo
    __copy_pics('Bluetooth', 'Bluetooth', last_backup_time, False)  # Bluetooth on Oppo
    __copy_pics('MIUI/ShareMe', 'Bluetooth', last_backup_time, False)  # Bluetooth on Xiaomi
    __copy_pics('Android/media/com.whatsapp/WhatsApp/Media', 'Whatsapp', last_backup_time, False)


def main():
    if not os.path.exists(DESTINATION_FOLDER):
        print('Nas is not connected! Path is {path}'.format(path=DESTINATION_FOLDER))
        sys.exit()

    if not FtpUtils.is_file_available(PATH_OF_LAST_BACKUP_FILE, NAME_OF_LAST_BACKUP_FILE):
        FtpUtils.create_file(PATH_OF_LAST_BACKUP_FILE, NAME_OF_LAST_BACKUP_FILE)

    last_backup_timestamp = FtpUtils.read_first_line(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE)
    backup_time_str = time.ctime(last_backup_timestamp)
    print('Last backup time was {timeStr} from {value}'.format(timeStr=backup_time_str, value=last_backup_timestamp))

    print('Have you copied the favourites pictures to the album "Best"? [Yes|No]')
    text = input("")
    if not str(text).lower().startswith("y"):
        sys.exit()

    __run_copy_process(last_backup_timestamp)

    FtpUtils.write_line(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE)


if __name__ == "__main__":
    # Get first argument
    # dir = sys.argv[1]
    main()
