# Runs a command, polls its peak working set and private bytes, prints one hbp row. usage: mem_probe.ps1 -Exe EXE -ArgLine "ARGS" -Out FILE ; integer only, json=0.
param([string]$Exe, [string]$ArgLine, [string]$Out)
$p = Start-Process -FilePath $Exe -ArgumentList $ArgLine -PassThru -NoNewWindow -RedirectStandardOutput $Out -RedirectStandardError ($Out + ".err")
$null = $p.Handle
try { $p.PriorityClass = 'BelowNormal' } catch {}
[int64]$peak = 0
[int64]$priv = 0
[int64]$samples = 0
while (-not $p.HasExited) {
    try {
        $p.Refresh()
        if ($p.PeakWorkingSet64 -gt $peak) { $peak = $p.PeakWorkingSet64 }
        if ($p.PrivateMemorySize64 -gt $priv) { $priv = $p.PrivateMemorySize64 }
        $samples++
    } catch {}
    Start-Sleep -Milliseconds 50
}
$p.WaitForExit()
"MEM_PROBE|exe=$Exe|args=$ArgLine|exit=$($p.ExitCode)|samples=$samples|peak_working_set_bytes=$peak|peak_private_bytes_sampled=$priv|json=0"
