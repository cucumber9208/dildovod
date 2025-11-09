@echo off
echo 🚀 Збірка програми в EXE...

pyinstaller --name="АналізаторНаказівЗСУ" ^
            --windowed ^
            --onefile ^
            --icon=icon.ico ^
            --add-data="patterns.json;." ^
            --hidden-import=typing ^
            --hidden-import=pathlib ^
            --hidden-import=threading ^
            --hidden-import=webbrowser ^
            --hidden-import=docx ^
            --hidden-import=PyPDF2 ^
            --hidden-import=pandas ^
            --hidden-import=openpyxl ^
            --hidden-import=pytesseract ^
            --hidden-import=PIL ^
            main.py

echo ✅ Збірка завершена!
echo 📁 EXE файл знаходиться в папці dist/
pause