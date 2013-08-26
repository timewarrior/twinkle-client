@echo off
SET SCRIPT_DIR=%~dp0..\twinkle-client
cd %SCRIPT_DIR%
python client.py %*
