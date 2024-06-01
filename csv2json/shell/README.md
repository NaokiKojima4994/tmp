以下は、PowerShell版とsh版のスクリプトのREADMEファイルです。

---

# CSVからJSONへの変換スクリプト

このリポジトリには、CSVファイルをJSON形式に変換するための2つのスクリプトが含まれています。一つはPowerShellで書かれており、もう一つはsh（Bash）で書かれています。どちらのスクリプトも、指定されたJSONファイルが存在しない場合に作成します。

## PowerShellスクリプト

### 前提条件

- PowerShell 5.1以上

### スクリプト: `ConvertCsvToJson.ps1`

### 説明

このスクリプトはCSVファイルをJSONファイルに変換します。JSONファイルが存在しない場合は、新しいファイルを作成します。

### 使用方法

1. スクリプトを `ConvertCsvToJson.ps1` として保存します。
2. PowerShellターミナルを開きます。
3. 以下のコマンドでスクリプトを実行します：

```powershell
.\ConvertCsvToJson.ps1 -csvFilePath "path\to\input.csv" -jsonFilePath "path\to\output.json"
```

### 例

```powershell
.\ConvertCsvToJson.ps1 -csvFilePath "input.csv" -jsonFilePath "output.json"
```

### スクリプトの内容

```powershell
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

# CSVの内容をJSONに変換
$jsonContent = $csvContent | ConvertTo-Json -Depth 100

# JSONファイルが存在しない場合、ファイルを作成する
if (-Not (Test-Path $jsonFilePath)) {
    New-Item -Path $jsonFilePath -ItemType File -Force
}

# JSONファイルに書き込む
$jsonContent | Out-File -FilePath $jsonFilePath

Write-Output "CSV file '$csvFilePath' has been converted to JSON and saved as '$jsonFilePath'"
```

## シェルスクリプト

### 前提条件

- Unix系環境（Linux、macOS、またはWSL上のWindows）
- `sh`シェル

### スクリプト: `convert.sh`

### 説明

このスクリプトはCSVファイルをJSONファイルに変換します。JSONファイルが存在しない場合は、新しいファイルを作成します。

### 使用方法

1. スクリプトを `convert.sh` として保存します。
2. スクリプトに実行権限を付与します：

```sh
chmod +x convert.sh
```

3. 以下のコマンドでスクリプトを実行します：

```sh
./convert.sh path/to/input.csv path/to/output.json
```

### 例

```sh
./convert.sh input.csv output.json
```

### スクリプトの内容

```sh
#!/bin/sh

# 第一引数をCSVファイルパス、第二引数をJSONファイルパスとして取得
csvFilePath=$1
jsonFilePath=$2

# CSVファイルの存在を確認
if [ ! -f "$csvFilePath" ]; then
    echo "CSV file '$csvFilePath' does not exist."
    exit 1
fi

# JSONファイルが存在しない場合、ファイルを作成
if [ ! -f "$jsonFilePath" ]; then
    touch "$jsonFilePath"
fi

# 空のJSONファイルを作成
echo "[" > "$jsonFilePath"

# CSVファイルを読み込み
{
  read header_line
  headers=$(echo $header_line | tr ',' ' ')
  isFirstRecord=true

  while IFS=, read -r $headers; do
    if [ "$isFirstRecord" = true ]; then
      isFirstRecord=false
    else
      echo "," >> "$jsonFilePath"
    fi

    echo "  {" >> "$jsonFilePath"

    fieldIndex=1
    for field in $headers; do
      value=$(eval echo \$$field | sed 's/"/\\"/g')
      if [ $fieldIndex -gt 1 ]; then
        echo "," >> "$jsonFilePath"
      fi
      echo "    \"$field\": \"$value\"" >> "$jsonFilePath"
      fieldIndex=$((fieldIndex + 1))
    done

    echo "  }" >> "$jsonFilePath"
  done
} < "$csvFilePath"

# JSONファイルの閉じ括弧を追加
echo "]" >> "$jsonFilePath"

echo "CSV file '$csvFilePath' has been converted to JSON and saved as '$jsonFilePath'"
```

## 注意事項

- CSVファイルが存在し、正しくフォーマットされていることを確認してください。
- どちらのスクリプトも、JSONファイルが既に存在する場合は上書きします。
- スクリプトは基本的なCSVパースのみを行い、フィールドにカンマや改行が含まれる場合などのエッジケースは処理しません。より堅牢なソリューションが必要な場合は、専用のCSVパースライブラリの使用を検討してください。