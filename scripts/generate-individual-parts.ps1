# Script to generate individual STL files for nutcracker enclosure
# Each part prints separately on 220x220mm bed

$openscad = "C:\Program Files\OpenSCAD\openscad.exe"
$scadFile = "D:\Nutcracker\Nutcracker\wwwroot\nutcracker-enclosure.scad"
$outputDir = "D:\Nutcracker\Nutcracker\wwwroot"

Write-Host "=== GENERATING INDIVIDUAL NUTCRACKER PARTS ===" -ForegroundColor Cyan
Write-Host ""

# Part 1: Main Box Base
Write-Host "1/5 Generating main box base..." -ForegroundColor Yellow
& $openscad -D 'render_part="box"' -o "$outputDir\nutcracker-box-base.stl" $scadFile
Write-Host "    ✓ nutcracker-box-base.stl" -ForegroundColor Green

# Part 2: Lid
Write-Host "2/5 Generating lid..." -ForegroundColor Yellow  
& $openscad -D 'render_part="lid"' -o "$outputDir\nutcracker-box-lid.stl" $scadFile
Write-Host "    ✓ nutcracker-box-lid.stl" -ForegroundColor Green

# Part 3: Display Left Half
Write-Host "3/5 Generating display left half..." -ForegroundColor Yellow
& $openscad -D 'render_part="display_left"' -o "$outputDir\nutcracker-display-left.stl" $scadFile
Write-Host "    ✓ nutcracker-display-left.stl" -ForegroundColor Green

# Part 4: Display Right Half
Write-Host "4/5 Generating display right half..." -ForegroundColor Yellow
& $openscad -D 'render_part="display_right"' -o "$outputDir\nutcracker-display-right.stl" $scadFile
Write-Host "    ✓ nutcracker-display-right.stl" -ForegroundColor Green

# Part 5: Display Cover
Write-Host "5/5 Generating display cover..." -ForegroundColor Yellow
& $openscad -D 'render_part="cover"' -o "$outputDir\nutcracker-display-cover.stl" $scadFile
Write-Host "    ✓ nutcracker-display-cover.stl" -ForegroundColor Green

Write-Host ""
Write-Host "=== ALL PARTS GENERATED! ===" -ForegroundColor Green
Write-Host ""
Write-Host "5 STL files created in: $outputDir"
Write-Host ""
Write-Host "Print order recommendation:"
Write-Host "  1. nutcracker-box-base.stl (~6-8 hours)"
Write-Host "  2. nutcracker-box-lid.stl (~3-4 hours)"
Write-Host "  3. nutcracker-display-left.stl (~4-5 hours)"
Write-Host "  4. nutcracker-display-right.stl (~4-5 hours)"
Write-Host "  5. nutcracker-display-cover.stl (~2-3 hours)"
