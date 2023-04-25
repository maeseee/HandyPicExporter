from datetime import datetime
import ftplib
import io
import os
from ftplib import FTP

import ImageUtils


def openFptConnection():
    ftp_server = "192.168.50.211"
    ftp_user = "android"
    ftp_pass = "mySweetHandyAccess"
    ftp_port = 2221

    ftp = FTP()
    ftp.connect(ftp_server, ftp_port)
    ftp.login(ftp_user, ftp_pass)

    return ftp


def closeFtpConnection(ftp):
    ftp.quit()


def readModificationDate(fullFilename):
    ftp = openFptConnection()

    mod_time = ftp.sendcmd("MDTM " + fullFilename)[4:]

    closeFtpConnection(ftp)
    return mod_time


def readFirstLine(fullFileName):
    ftp = openFptConnection()

    with io.StringIO() as file_obj:
        ftp.retrlines('RETR ' + fullFileName, file_obj.write)
        fileContents = file_obj.getvalue()

    closeFtpConnection(ftp)
    return float(fileContents)


def isFileAvailable(directory, filename):
    ftp = openFptConnection()

    ftp.cwd(directory)
    file_list = ftp.nlst()
    fileAvailable = filename in file_list

    closeFtpConnection(ftp)
    return fileAvailable


def createFile(directory, filename):
    ftp = openFptConnection()

    ftp.cwd(directory)
    with open(filename, 'w') as file:
        file.write('0')

    closeFtpConnection(ftp)


def __directory_exists(ftp, directory):
    try:
        ftp.cwd(directory)
        number_subdirectories = directory.count('/')
        for i in range(number_subdirectories + 1):
            ftp.cwd("..")
        return True
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            print("Folder " + directory + " does not exist")
            return False
        else:
            raise


def copy_image_files(sourceDirectory, destinationDirectory, lastBackupTimestamp, isFavorit):
    ftp = openFptConnection()

    source_directory_exists = __directory_exists(ftp, sourceDirectory)
    if not source_directory_exists:
        return

    ftp.cwd(sourceDirectory)
    ftp.sendcmd('TYPE I')

    fileList = []
    try:
        fileList = ftp.nlst()
        print(fileList)
    except ftplib.error_perm as resp:
        if str(resp) == "550 No files found":
            print("No files in this directory")
        else:
            raise

    # Copy each file to the local directory
    for filename in fileList:
        if filename.endswith('.jpg') or \
                filename.endswith('.jpeg') or \
                filename.endswith('.png') or \
                filename.endswith('.giv') or \
                filename.endswith('.mp4'):
            filePath = destinationDirectory + filename
            if os.path.exists(filePath):
                print(filePath + ' already copied')
                continue

            # Get the modification date of the file
            modificationTimeStr = ftp.sendcmd('MDTM ' + filename)[4:]
            modificationTime = int(float(modificationTimeStr))
            modificationDateTime = datetime.strptime(str(modificationTime), '%Y%m%d%H%M%S')
            # convert the datetime object to an integer representing the number of seconds since 1970
            modificationTimestamp = int(modificationDateTime.timestamp())

            if modificationTimestamp < lastBackupTimestamp:
                continue

            with open(filePath, "wb") as f:
                ftp.retrbinary("RETR " + filename, f.write)

            if isFavorit:
                ImageUtils.five_stars_to_file(filePath)
        else:
            print("File " + filename + " has been ignored!")
