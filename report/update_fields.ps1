# Opens the report in Word, updates the table of contents, list of figures, list of tables and page numbers,
# saves the document and exports a PDF next to it.
param([string]$Docx = "$PSScriptRoot\EcoServe_AI_Report.docx")
$pdf = [System.IO.Path]::ChangeExtension($Docx, ".pdf")
$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($Docx)
    $doc.Fields.Update() | Out-Null
    foreach ($toc in $doc.TablesOfContents) { $toc.Update() }
    $doc.Repaginate()
    foreach ($toc in $doc.TablesOfContents) { $toc.UpdatePageNumbers() }
    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17)
    "pages: " + $doc.ComputeStatistics(2)
    "words: " + $doc.ComputeStatistics(0)
    $doc.Close()
} finally {
    $word.Quit()
}
"exported $pdf"
