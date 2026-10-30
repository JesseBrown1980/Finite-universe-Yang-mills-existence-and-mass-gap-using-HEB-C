# Read-only: hold a handle on the 3x4 pilot roomschur.exe process; poll every 60 s; final reading after exit, before closing the handle.
Add-Type -Namespace W -Name P -MemberDefinition @'
[StructLayout(LayoutKind.Sequential)] public struct PMC { public uint cb; public uint PageFaultCount; public UIntPtr PeakWorkingSetSize; public UIntPtr WorkingSetSize; public UIntPtr QuotaPeakPagedPoolUsage; public UIntPtr QuotaPagedPoolUsage; public UIntPtr QuotaPeakNonPagedPoolUsage; public UIntPtr QuotaNonPagedPoolUsage; public UIntPtr PagefileUsage; public UIntPtr PeakPagefileUsage; }
[DllImport("kernel32.dll")] public static extern IntPtr OpenProcess(uint a, bool i, int pid);
[DllImport("kernel32.dll")] public static extern bool CloseHandle(IntPtr h);
[DllImport("psapi.dll", SetLastError=true)] public static extern bool GetProcessMemoryInfo(IntPtr h, out PMC c, uint cb);
'@
$o = 'D:\ym-3x4-room-run\pilot3x4\PILOT-MEM.hbp'
$p = Get-Process roomschur | Select-Object -First 1
$h = [W.P]::OpenProcess(0x1410, $false, $p.Id)
function Write-PassBMem($state) { $c = New-Object W.P+PMC; $c.cb = [Runtime.InteropServices.Marshal]::SizeOf($c); $ok = [W.P]::GetProcessMemoryInfo($h, [ref]$c, $c.cb)
  Add-Content $o ("PILOT_PROC_MEM|scope=pilot_roomschur_process_only|pid={0}|state={1}|t={2}|ok={3}|peak_working_set_bytes={4}|working_set_bytes={5}|peak_pagefile_bytes={6}|json=0" -f $p.Id, $state, (Get-Date -Format s), [int]$ok, $c.PeakWorkingSetSize, $c.WorkingSetSize, $c.PeakPagefileUsage) }
while (-not $p.HasExited) { Write-PassBMem 'running'; Start-Sleep 60 }
Write-PassBMem 'exited_final'
[void][W.P]::CloseHandle($h)
