param (
    [string]$csvFilePath,
    [string]$jsonFilePath
)

# CSVファイルの存在を確認
if (-Not (Test-Path $csvFilePath)) {
    Write-Error "CSV file '$csvFilePath' does not exist."
    exit 1
}

# CSVファイルを読み込む
$csvContent = Import-Csv -Path $csvFilePath

# 空のJSONオブジェクトを作成
$jsonArray = @()

# 各行を処理
foreach ($row in $csvContent) {
    $jsonObject = @{}

    foreach ($key in $row.PSObject.Properties.Name) {
        $value = $row.$key
        if ($value -ne "") {
            $jsonObject[$key] = $value
        }
    }

    $jsonArray += $jsonObject
}

# JSONオブジェクトをJSON形式に変換
$jsonContent = $jsonArray | ConvertTo-Json -Depth 100

# JSONファイルが存在しない場合、ファイルを作成する
if (-Not (Test-Path $jsonFilePath)) {
    New-Item -Path $jsonFilePath -ItemType File -Force
}

# JSONファイルに書き込む
$jsonContent | Out-File -FilePath $jsonFilePath

Write-Output "CSV file '$csvFilePath' has been converted to JSON and saved as '$jsonFilePath'"
