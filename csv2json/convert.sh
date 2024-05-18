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