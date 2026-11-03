# Samples the reader's memory and priority while it runs. Writes rows to OUT. Read only. Integer only, json=0.
param([string]$Name, [string]$Out, [int]$Seconds = 15)
[int64]$peakWs = 0; [int64]$peakPriv = 0; $prio = ''; [int64]$n = 0
for ($i = 0; $i -lt 60; $i++) { if (Get-Process $Name -ErrorAction SilentlyContinue) { break }; Start-Sleep -Seconds 1 }
while ($p = Get-Process $Name -ErrorAction SilentlyContinue | Select-Object -First 1) {
    try {
        if ($p.PeakWorkingSet64 -gt $peakWs) { $peakWs = $p.PeakWorkingSet64 }
        if ($p.PrivateMemorySize64 -gt $peakPriv) { $peakPriv = $p.PrivateMemorySize64 }
        $prio = "$($p.PriorityClass)"
        $n++
    } catch {}
    Start-Sleep -Seconds $Seconds
}
"READER_MEM|name=$Name|samples=$n|peak_working_set_bytes=$peakWs|peak_private_bytes_sampled=$peakPriv|priority=$prio|json=0" | Out-File -FilePath $Out -Encoding ascii
