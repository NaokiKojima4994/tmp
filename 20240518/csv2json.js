const fs = require('fs');
const readline = require('readline');

// 入力ファイルと出力ファイルのパス
const inputFile = 'input.csv';
const outputFile = 'output.json';

// CSVファイルを読み込むストリームを作成
const readStream = fs.createReadStream(inputFile);

// readlineインターフェースを作成
const rl = readline.createInterface({
  input: readStream,
  crlfDelay: Infinity
});

const results = [];
let headers = [];

// 各行を処理
rl.on('line', (line) => {
  // CSVの行をカンマで分割
  const values = line.split(',');

  // ヘッダー行を取得
  if (headers.length === 0) {
    headers = values;
  } else {
    // ヘッダーと各行の値をマッピング
    const obj = {};
    headers.forEach((header, index) => {
      obj[header] = values[index];
    });
    results.push(obj);
  }
});

// ファイル読み取り終了時の処理
rl.on('close', () => {
  // JSONファイルに変換して保存
  fs.writeFileSync(outputFile, JSON.stringify(results, null, 2));
  console.log('CSV file has been converted to JSON and saved as output.json');
});