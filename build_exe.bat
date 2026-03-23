@echo off
setlocal

set WINDOW_MODE=--windowed
if /I "%~1"=="console" set WINDOW_MODE=--console

set APP_VERSION=0.0.0
if exist VERSION set /p APP_VERSION=<VERSION

for /f "tokens=1-3 delims=." %%a in ("%APP_VERSION%") do (
  set VER_MAJOR=%%a
  set VER_MINOR=%%b
  set VER_PATCH=%%c
)
if "%VER_MAJOR%"=="" set VER_MAJOR=0
if "%VER_MINOR%"=="" set VER_MINOR=0
if "%VER_PATCH%"=="" set VER_PATCH=0

set BUILD_NUM=0
if exist BUILD_NUMBER set /p BUILD_NUM=<BUILD_NUMBER
set /a BUILD_NUM=BUILD_NUM+1
> BUILD_NUMBER echo %BUILD_NUM%

set EXE_NAME=NFDtoNFC-v%APP_VERSION%-b%BUILD_NUM%

> version_info.txt echo VSVersionInfo(
>> version_info.txt echo   ffi=FixedFileInfo(
>> version_info.txt echo     filevers=(%VER_MAJOR%, %VER_MINOR%, %VER_PATCH%, %BUILD_NUM%),
>> version_info.txt echo     prodvers=(%VER_MAJOR%, %VER_MINOR%, %VER_PATCH%, %BUILD_NUM%),
>> version_info.txt echo     mask=0x3f,
>> version_info.txt echo     flags=0x0,
>> version_info.txt echo     OS=0x40004,
>> version_info.txt echo     fileType=0x1,
>> version_info.txt echo     subtype=0x0,
>> version_info.txt echo     date=(0, 0)
>> version_info.txt echo   ^),
>> version_info.txt echo   kids=[
>> version_info.txt echo     StringFileInfo([
>> version_info.txt echo       StringTable('040904B0', [
>> version_info.txt echo         StringStruct('CompanyName', ''),
>> version_info.txt echo         StringStruct('FileDescription', 'NFD to NFC Hangul filename fixer'),
>> version_info.txt echo         StringStruct('FileVersion', '%APP_VERSION%.%BUILD_NUM%'),
>> version_info.txt echo         StringStruct('InternalName', 'NFDtoNFC'),
>> version_info.txt echo         StringStruct('OriginalFilename', '%EXE_NAME%.exe'),
>> version_info.txt echo         StringStruct('ProductName', 'NFDtoNFC'),
>> version_info.txt echo         StringStruct('ProductVersion', '%APP_VERSION%.%BUILD_NUM%')
>> version_info.txt echo       ]^)
>> version_info.txt echo     ]^),
>> version_info.txt echo     VarFileInfo([VarStruct('Translation', [1033, 1200])])
>> version_info.txt echo   ]
>> version_info.txt echo ^)

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 goto :error

echo [2/3] Building executable with PyInstaller...
if exist assets\icon.ico (
  pyinstaller --noconfirm --clean --onefile %WINDOW_MODE% --name %EXE_NAME% --icon assets\icon.ico --version-file version_info.txt --add-data "config;config" --add-data "assets;assets" --add-data "VERSION;." --add-data "BUILD_NUMBER;." --hidden-import pystray --hidden-import pystray._win32 --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageDraw --hidden-import watchdog.events --hidden-import watchdog.observers --collect-submodules pystray src\main.py
) else (
  pyinstaller --noconfirm --clean --onefile %WINDOW_MODE% --name %EXE_NAME% --version-file version_info.txt --add-data "config;config" --add-data "assets;assets" --add-data "VERSION;." --add-data "BUILD_NUMBER;." --hidden-import pystray --hidden-import pystray._win32 --hidden-import PIL --hidden-import PIL.Image --hidden-import PIL.ImageDraw --hidden-import watchdog.events --hidden-import watchdog.observers --collect-submodules pystray src\main.py
)
if errorlevel 1 goto :error

echo [3/3] Done. Check dist\%EXE_NAME%.exe
exit /b 0

:error
echo Build failed.
exit /b 1
