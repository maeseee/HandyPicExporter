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


def copyImageFiles(sourceDirectory, destinationDirectory, lastBackupTimestamp, isFavorit):
    ftp = openFptConnection()

    try:
        ftp.cwd(sourceDirectory)
    except ftplib.error_perm as e:
        if str(e).startswith("550"):
            print("Folder " + sourceDirectory + " does not exist")
            return
        else:
            raise e
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
        if filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.png') or filename.endswith(
                '.giv' or filename.endswith('.mp4')):
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
                print('Add favorit picture ' + filePath)
                ImageUtils.fiveStarsToFile(filePath)
        else:
            print("File " + filename + " has been ignored!")
