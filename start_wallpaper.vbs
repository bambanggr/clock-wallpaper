Dim WshShell, scriptDir, venvPython, scriptPath
Set WshShell = CreateObject("WScript.Shell")
scriptDir = Replace(WScript.ScriptFullName, "start_wallpaper.vbs", "")
venvPython = scriptDir & ".venv\Scripts\pythonw.exe"
scriptPath = scriptDir & "clock_wallpaper.py"

' Use venv pythonw if available, fall back to system pythonw
Dim fso
Set fso = CreateObject("Scripting.FileSystemObject")
If Not fso.FileExists(venvPython) Then
    venvPython = "pythonw"
End If

WshShell.Run """" & venvPython & """ """ & scriptPath & """", 0, False
