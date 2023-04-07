@echo off
set /p url=Enter URL To scrap: 
scrapy runspider "YouTube-spider.py" -a start_urls=%url% -o output.json
python Streem-to-vlc.py
set regKey=HKEY_LOCAL_MACHINE\SOFTWARE\VideoLAN\VLC
set regValue=InstallDir
set playlist_folder=%cd%
for /f "tokens=2*" %%a in ('reg query "%regKey%" /v "%regValue%" ^| findstr "%regValue%"') do set "installDir=%%b"


cd %installDir%
vlc "%playlist_folder%\playlist.m3u"
del "output.json"
