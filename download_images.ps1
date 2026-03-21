# LogiCart - Auto Image Downloader for Windows
# Double-click this file OR run in PowerShell:
#   powershell -ExecutionPolicy Bypass -File download_images.ps1
#
# This downloads real product images from Unsplash (free, no login needed)
# and saves them to:  media\shop\images\

$saveDir = Join-Path $PSScriptRoot "media\shop\images"
if (!(Test-Path $saveDir)) { New-Item -ItemType Directory -Path $saveDir -Force | Out-Null }

$images = @(
    # Electronics
    @{ file="sony-wh1000xm5.jpg";         url="https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&q=85&fit=crop" },
    @{ file="apple-ipad-air.jpg";          url="https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=85&fit=crop" },
    @{ file="samsung-qled-tv.jpg";         url="https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=600&q=85&fit=crop" },
    @{ file="mi-robot-vacuum.jpg";         url="https://images.unsplash.com/photo-1600857062241-98e5dba7f025?w=600&q=85&fit=crop" },
    @{ file="bose-qc45.jpg";              url="https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=600&q=85&fit=crop" },
    @{ file="dji-mini-4-pro.jpg";          url="https://images.unsplash.com/photo-1579829366248-204fe8413f31?w=600&q=85&fit=crop" },
    @{ file="oneplus-13.jpg";              url="https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&q=85&fit=crop" },
    @{ file="logitech-mx-master.jpg";      url="https://images.unsplash.com/photo-1527814050087-3793815479db?w=600&q=85&fit=crop" },

    # Fashion
    @{ file="nike-air-max-270.jpg";        url="https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=85&fit=crop" },
    @{ file="levis-511-jeans.jpg";         url="https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&q=85&fit=crop" },
    @{ file="adidas-ultraboost.jpg";       url="https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&q=85&fit=crop" },
    @{ file="rayban-aviator.jpg";          url="https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=85&fit=crop" },
    @{ file="fossil-gen6-watch.jpg";       url="https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&q=85&fit=crop" },
    @{ file="zara-blazer.jpg";             url="https://images.unsplash.com/photo-1594938298603-c8148c4b4357?w=600&q=85&fit=crop" },

    # Beauty
    @{ file="dyson-airwrap.jpg";           url="https://images.unsplash.com/photo-1522338242992-e1a54906a8da?w=600&q=85&fit=crop" },
    @{ file="ordinary-skincare.jpg";       url="https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=600&q=85&fit=crop" },
    @{ file="philips-trimmer.jpg";         url="https://images.unsplash.com/photo-1621607512214-68297480165e?w=600&q=85&fit=crop" },
    @{ file="mac-studio-fix.jpg";          url="https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=600&q=85&fit=crop" },

    # Home
    @{ file="instant-pot-duo.jpg";         url="https://images.unsplash.com/photo-1585515320310-259814833e62?w=600&q=85&fit=crop" },
    @{ file="dyson-v15-vacuum.jpg";        url="https://images.unsplash.com/photo-1558317374-067fb5f30001?w=600&q=85&fit=crop" },
    @{ file="philips-airfryer.jpg";        url="https://images.unsplash.com/photo-1648079866318-07d074a9e8cc?w=600&q=85&fit=crop" },
    @{ file="ikea-kallax.jpg";             url="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=600&q=85&fit=crop" },

    # Sports
    @{ file="decathlon-mtb.jpg";           url="https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=600&q=85&fit=crop" },
    @{ file="yoga-mat.jpg";                url="https://images.unsplash.com/photo-1601925228008-8f4c7f49f7b8?w=600&q=85&fit=crop" },
    @{ file="wilson-tennis-racket.jpg";    url="https://images.unsplash.com/photo-1617883861744-45b47a8c7e6c?w=600&q=85&fit=crop" },

    # Books
    @{ file="atomic-habits.jpg";           url="https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=85&fit=crop" },
    @{ file="deep-work.jpg";               url="https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=600&q=85&fit=crop" },
    @{ file="zero-to-one.jpg";             url="https://images.unsplash.com/photo-1589998059171-988d887df646?w=600&q=85&fit=crop" },

    # Toys
    @{ file="lego-bugatti.jpg";            url="https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=600&q=85&fit=crop" },
    @{ file="nintendo-switch-lite.jpg";    url="https://images.unsplash.com/photo-1578303512597-81e6cc155b3e?w=600&q=85&fit=crop" }
)

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  LogiCart - Downloading 30 Product Images" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Saving to: $saveDir" -ForegroundColor Gray
Write-Host ""

$ok = 0
$fail = 0
$client = New-Object System.Net.WebClient
$client.Headers.Add("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)")

for ($i = 0; $i -lt $images.Count; $i++) {
    $item = $images[$i]
    $dest = Join-Path $saveDir $item.file
    $num  = $i + 1

    # Skip if already downloaded
    if ((Test-Path $dest) -and (Get-Item $dest).Length -gt 5000) {
        Write-Host "  [$('{0:D2}' -f $num)/30]  SKIP  $($item.file)  (exists)" -ForegroundColor DarkGray
        $ok++
        continue
    }

    try {
        $client.DownloadFile($item.url, $dest)
        $size = [math]::Round((Get-Item $dest).Length / 1KB)
        Write-Host "  [$('{0:D2}' -f $num)/30]  OK    $($item.file)  ($($size)KB)" -ForegroundColor Green
        $ok++
        Start-Sleep -Milliseconds 200
    } catch {
        Write-Host "  [$('{0:D2}' -f $num)/30]  FAIL  $($item.file)" -ForegroundColor Red
        Write-Host "          $_" -ForegroundColor DarkRed
        $fail++
    }
}

$client.Dispose()

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Done!  $ok downloaded   $fail failed" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

if ($ok -gt 0) {
    Write-Host "  Next step - run this in your project folder:" -ForegroundColor Yellow
    Write-Host "    python add_images.py" -ForegroundColor White
    Write-Host ""
}

Write-Host "  Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
