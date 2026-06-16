Dim WshShell, scriptDir, pythonExe, scriptPath
Set WshShell = CreateObject("WScript.Shell")
scriptDir = Replace(WScript.ScriptFullName, "start_wallpaper.vbs", "")
scriptPath = scriptDir & "clock_wallpaper.py"

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

' Prefer venv python, fall back to system python
Dim venvPython
venvPython = scriptDir & ".venv\Scripts\python.exe"
If fso.FileExists(venvPython) Then
    pythonExe = venvPython
Else
    pythonExe = "python"
End If

' Run hidden (0 = hidden window, False = don't wait)
WshShell.Run """" & pythonExe & """ """ & scriptPath & """", 0, False
