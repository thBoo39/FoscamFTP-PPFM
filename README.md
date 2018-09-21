# Foscam camera FTP post process file manager (Foscam FTP-PPFM)

File names produced by FTP feature of Foscam camera FI9800p is in the format 'MDAlarm_yyyymmdd-hhmmss.jpg' and sent into a single folder. If there are hundreds of image files not sorted, it becomes chaotic. Often, it is convenient if files are placed in folders in date format.

This python code solves the problem. It scans the FTP created folder, sorts the image files into folders by date. It can also delete old images past a specified days.

I use MotionEye on DietPi (Raspberry Pi) for home surveillance system. I found Foscam camera motion detection works better than the MotionEye motion detection. However, now it doesn't sort image files as MotionEye does. So I created this Python script. It works good with a scheduler like Cron.

## Example

**Before:**

Foscam FTP sends image files into a folder ('Out' in this case) followed by Foscam generated names (something like 'FI9800P_00123E45E060/snap').

```
ls Out/FI9800P_00123E45E060/snap
MDAlarm_20180914-111429.jpg  MDAlarm_20180914-111435.jpg MDAlarm_20180913-101415.jpg  MDAlarm_20180913-101418.jpg MDAlarm_20180913-101421.jpg  MDAlarm_20180912-103040.jpg
```
There are 6 files with 3 different dates, 20180914, 20180913, and 20180912.

**After:**

Run by specifying the source folder (Out/FI9800P_00123E45E060/snap) with option '-s' and the destination folder (Uploads) with option '-d', for example:
```
python FoscamFTP-PPFM.py -s Out/FI9800P_00123E45E060/snap -d Uploads
```
Alternatively,
```
chmod +x FoscamFTP-PPFM.py
./FoscamFTP-PPFM.py -s Out/FI9800P_00123E45E060/snap -d Uploads
```
Then you will have image files nicely sorted into folders by date.
```
ls Uploads
20180914  20180913  20180912

ls Uploads/20180914
111429.jpg  111435.jpg

ls Uploads/20180913
101415.jpg  101418.jpg 101421.jpg

ls Uploads/20180912
103040.jpg
```


## Usage
```
usage: FoscamFTP-PPFM.py [-h] -s SRC -d DST [--day DAY] [--foscam-format FOSCAM_FORMAT]
                         [--folder-format FOLDER_FORMAT] [--file-format FILE_FORMAT]

Foscam FTP post process file manager (PPFM)

optional arguments:
  -h, --help            show this help message and exit
  -s SRC, --src SRC     Source Foscam FTP folder
  -d DST, --dst DST     Destination folder
  --day DAY             Days to keep image files (default: 7 days)
  --foscam-format FOSCAM_FORMAT
                        Foscam FTP file name format (default:
                        MDAlarm_%Y%m%d-%H%M%S.jpg)
  --folder-format FOLDER_FORMAT
                        folder name format (default: %Y%m%d)
  --file-format FILE_FORMAT
                        file name format (default: %H%M%S.jpg)
  --keep-files          keep the original image files if specified
```


## Prerequisites

Confirmed working with Python 2.7 or Python 3.7

## Installing

Simply download FoscamPPFM.py and DirStateCmp.py into a same folder.

It is useful to run this code using scheduler like cron in linux. So I run:
```
crontab -e
```
then add the following line (assuming the script in FoscamPPFM folder):
```
0 */1 * * * python /home/pi/FoscamFTP-PPFM/FoscamFTP-PPFM.py -s /home/pi/Out/FI9800P_00123E45E060/snap/ -d /home/pi/Uploads/
```
This will check Foscam created FTP folder every hour and copy files into Uploads folder sorted by date.

I also use rclone which syncs a folder content to a cloud storage like DropBox. Quite useful.
