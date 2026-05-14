param(
    [Parameter(Mandatory = $true)]
    [string]$InputDocx,
    [Parameter(Mandatory = $true)]
    [string]$OutputPdf
)

$ErrorActionPreference = "Stop"

$inputPath = (Resolve-Path -LiteralPath $InputDocx).Path
$outputPath = [System.IO.Path]::GetFullPath($OutputPdf)
$outputDir = Split-Path -Parent $outputPath
if (-not (Test-Path -LiteralPath $outputDir)) {
    New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
}

$wps = $null
$doc = $null

function Try-SetBool {
    param(
        [object]$Target,
        [string]$Name,
        [bool]$Value
    )
    try {
        if ($null -ne $Target) {
            $Target.$Name = $Value
        }
    }
    catch {
    }
}

function Hide-Formatting-Marks {
    param([object]$Application)
    if ($null -eq $Application) {
        return
    }
    $optionNames = @(
        "ShowAll",
        "ShowTabs",
        "ShowSpaces",
        "ShowParagraphs",
        "ShowParagraphMarks",
        "ShowHiddenText",
        "ShowObjectAnchors",
        "ShowBookmarks",
        "ShowTextBoundaries",
        "ShowOptionalBreaks"
    )
    foreach ($name in $optionNames) {
        Try-SetBool $Application.Options $name $false
    }
    try {
        $window = $Application.ActiveWindow
        foreach ($name in $optionNames) {
            Try-SetBool $window.View $name $false
        }
    }
    catch {
    }
}

try {
    $wps = New-Object -ComObject kwps.Application
    $wps.Visible = $false
    $wps.DisplayAlerts = 0
    Hide-Formatting-Marks $wps
    $doc = $wps.Documents.Open($inputPath, $false, $true)
    Try-SetBool $doc "TrackRevisions" $false
    Try-SetBool $doc "ShowRevisions" $false
    Hide-Formatting-Marks $wps
    $doc.ExportAsFixedFormat($outputPath, 17)
}
finally {
    if ($doc -ne $null) {
        $doc.Close($false)
    }
    if ($wps -ne $null) {
        $wps.Quit()
    }
}

Write-Output $outputPath
