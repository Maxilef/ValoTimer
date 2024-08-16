pour faire le build (exe) : pyinstaller --onefile --add-data "C:\Users\maxim\IdeaProjects\ValoTimer\icon.ico;." --hidden-import pygetwindow main.py

pyinstaller --onefile --add-data "C:\\Users\\maxim\\IdeaProjects\\ValoTimer\\icon.ico;." --hidden-import pandas --additional-hooks-dir=hooks main.py


pour executer le .exe : dist/main.exe
