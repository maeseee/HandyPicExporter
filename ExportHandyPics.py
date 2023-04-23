#! /usr/bin/python

import os
import sys
import time

import FtpUtils

PATH_OF_LAST_BACKUP_FILE = 'DCIM/'  # Do not save it on the root of the phone as it automatically gets deleted
NAME_OF_LAST_BACKUP_FILE = 'LastBackup.txt'
#DESTINATION_FOLDER = 'C:\\Users\\maese\\Bilder\\FromHandy\\'
DESTINATION_FOLDER = 'C:\\Users\\maese\\Documents\\Temp\\'

def copyPics(sourceDirectory, destinationFolder, lastBackupTime, isFavorit):
    destinationDirectory = DESTINATION_FOLDER + destinationFolder + "\\"
    print('Copy picturs from ' + sourceDirectory + ' to ' + destinationDirectory)
    if not os.path.exists(destinationDirectory):
        os.makedirs(destinationDirectory)

    FtpUtils.copyImageFiles(sourceDirectory, destinationDirectory, lastBackupTime, isFavorit)


def runCopyProcess(lastBackupTime):
    copyPics('DCIM/MyAlbums/Best', 'Camera', lastBackupTime, True)  # Favourites on Oppo
    copyPics('MIUI/Gallery/cloud/owner/best', 'Camera', lastBackupTime, True)  # Favourites on Xiaomi
    copyPics('MIUI/Gallery/cloud/owner', 'Camera', lastBackupTime, True)  # Albums on Xiaomi
    copyPics('DCIM', 'Camera', lastBackupTime, False)
    copyPics('Pictures', 'Signal', lastBackupTime, False)  # Signal on Oppo
    copyPics('Bluetooth', 'Bluetooth', lastBackupTime, False)  # Bluetooth on Oppo
    copyPics('MIUI/ShareMe', 'Bluetooth', lastBackupTime, False)  # Bluetooth on Xiaomi
    copyPics('WhatsApp/Media/WhatsApp Images', 'Whatsapp', lastBackupTime, False)
    copyPics('WhatsApp/Media/WhatsApp Video', 'Whatsapp', lastBackupTime, False)


def main():
    # Check if destination folder is available
    if not os.path.exists(DESTINATION_FOLDER):
        print('Nas is not connected! Path is {path}'.format(path=DESTINATION_FOLDER))
        sys.exit()

    if not FtpUtils.isFileAvailable(PATH_OF_LAST_BACKUP_FILE, NAME_OF_LAST_BACKUP_FILE):
        FtpUtils.createFile(PATH_OF_LAST_BACKUP_FILE, NAME_OF_LAST_BACKUP_FILE)

    lastBackupTimestamp = FtpUtils.readFirstLine(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE)
    backupTimeStr = time.ctime(lastBackupTimestamp)
    print('Last backup time was {timeStr} from {value}'.format(timeStr=backupTimeStr, value=lastBackupTimestamp))

    print('Have you copied the favourites pictures to the album "Best"? [Yes|No]')
    text = input("")
    if not "y" in str(text).lower():
        sys.exit()

    runCopyProcess(lastBackupTimestamp)

    modificationDate = FtpUtils.readModificationDate(PATH_OF_LAST_BACKUP_FILE + NAME_OF_LAST_BACKUP_FILE)
    print('Modification date is {modDate}'.format(modDate=modificationDate))


if __name__ == "__main__":
    # Get first argument
    # dir = sys.argv[1]
    main()
