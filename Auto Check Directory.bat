@echo off
set output_file=daftar_file_game.txt
echo Menghitung daftar file... > %output_file%
echo -------------------------------------- >> %output_file%
echo DIREKTORI: %cd% >> %output_file%
echo -------------------------------------- >> %output_file%
dir /S /O:S >> %output_file%
echo. >> %output_file%
echo Selesai! Daftar file disimpan di %output_file%
pause