Dim WshShell, scriptDir, pythonExe, scriptPath
Set WshShell = CreateObject("WScript.Shell")

Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName) & "\"
scriptPath = scriptDir & "clock_wallpaper.py"

' Prefer venv pythonw (no console window), fall back to system python
Dim venvPythonw
venvPythonw = scriptDir & ".venv\Scripts\pythonw.exe"
If fso.FileExists(venvPythonw) Then
    pythonExe = venvPythonw
Else
    pythonExe = "python"
End If

' Run hidden (0 = hidden window, False = don't wait)
WshShell.Run Chr(34) & pythonExe & Chr(34) & " " & Chr(34) & scriptPath & Chr(34), 0, False
