param(
    [Parameter(Mandatory = $true)][string]$TitleMatch,
    [Parameter(Mandatory = $true)][string]$Out,
    [int]$Delay = 2,
    [switch]$Maximize
)

Add-Type -AssemblyName System.Drawing

Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win {
    [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
    [DllImport("user32.dll")] public static extern bool SetProcessDPIAware();
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdc, uint flags);
    [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
}
"@

[void][Win]::SetProcessDPIAware()

$proc = Get-Process | Where-Object { $_.MainWindowTitle -like "*$TitleMatch*" } |
        Sort-Object StartTime -Descending | Select-Object -First 1
if (-not $proc) { Write-Error "no window matching '$TitleMatch'"; exit 1 }

$h = $proc.MainWindowHandle
if ($Maximize) { [void][Win]::ShowWindow($h, 3) }
[void][Win]::SetForegroundWindow($h)
Start-Sleep -Seconds $Delay

$r = New-Object Win+RECT
[void][Win]::GetWindowRect($h, [ref]$r)
$w = $r.Right - $r.Left
$hgt = $r.Bottom - $r.Top
if ($w -le 0 -or $hgt -le 0) { Write-Error "bad window rect"; exit 1 }

# PrintWindow with PW_RENDERFULLCONTENT asks the window to draw itself into our
# bitmap. Unlike CopyFromScreen it captures that window only, so nothing else on
# the desktop can end up in the image if the window is not actually on top.
$bmp = New-Object System.Drawing.Bitmap $w, $hgt
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
$ok = [Win]::PrintWindow($h, $hdc, 2)
$g.ReleaseHdc($hdc)
if (-not $ok) {
    $g.CopyFromScreen($r.Left, $r.Top, 0, 0, (New-Object System.Drawing.Size $w, $hgt))
}
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"captured '$($proc.MainWindowTitle)' -> $Out ($w x $hgt, PrintWindow=$ok)"
