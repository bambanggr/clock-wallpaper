Dim WshShell, fso, scriptDir, pythonExe, managePy
Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

scriptDir = fso.GetParentFolderName(WScript.ScriptFullName) & "\"
managePy  = scriptDir & "manage.py"

Dim venvPython
venvPython = scriptDir & ".venv\Scripts\python.exe"
If fso.FileExists(venvPython) Then
    pythonExe = venvPython
Else
    pythonExe = "python"
End If

' window=1 agar GUI muncul (bukan hidden), False = jangan tunggu
WshShell.Run Chr(34) & pythonExe & Chr(34) & " " & Chr(34) & managePy & Chr(34), 1, False
