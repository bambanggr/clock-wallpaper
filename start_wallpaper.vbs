Dim WshShell, scriptPath
Set WshShell = CreateObject("WScript.Shell")
scriptPath = Replace(WScript.ScriptFullName, "start_wallpaper.vbs", "clock_wallpaper.py")
WshShell.Run "pythonw """ & scriptPath & """", 0, False
