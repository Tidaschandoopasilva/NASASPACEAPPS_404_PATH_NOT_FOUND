@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Team 404 - Automatically Create GitHub Repo and Push
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0CREATE_AND_PUBLISH_GITHUB.ps1"
