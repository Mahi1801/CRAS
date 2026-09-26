$action = New-ScheduledTaskAction -Execute "pythonw.exe" -Argument "`"$((Get-Location).Path)\main.py`"" -WorkingDirectory (Get-Location).Path
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName "CRAS_ActivityTracker" -Action $action -Trigger $trigger -Settings $settings -Description "CRAS Continuous Activity Tracker" -Force
Write-Host "CRAS installed. It will start at next login."