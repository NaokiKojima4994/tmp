# データ生成プログラム

このプログラムは、指定された顧客数と各顧客に紐づく注文数を生成し、CSVファイルとして保存します。

## 必要な準備

1. [Rust](https://www.rust-lang.org/ja/tools/install)がインストールされていることを確認してください。
2. プロジェクトのディレクトリを作成し、そこにプログラムファイルを保存します。

## プログラムファイルの準備

以下は、Rust版のデータ生成プログラムに対応するテストコードを含む完全なサンプルです。

### メインプログラム (`main.rs`)

まず、メインプログラムのコードを `src/main.rs` に保存します。

```rust
use rand::distributions::Alphanumeric;
use rand::{thread_rng, Rng};
use rand::seq::SliceRandom;
use std::env;
use std::fs::File;
use std::io::{self, Write};
use std::path::Path;

#[derive(Debug)]
struct Customer {
    id: usize,
    name: String,
    email: String,
}

#[derive(Debug)]
struct Order {
    id: usize,
    customer_id: usize,
    product_name: String,
    quantity: usize,
    order_date: String,
    status: String,
}

fn random_string(n: usize) -> String {
    thread_rng().sample_iter(&Alphanumeric).take(n).map(char::from).collect()
}

fn generate_customers(num_customers: usize) -> Vec<Customer> {
    (1..=num_customers)
        .map(|i| Customer {
            id: i,
            name: random_string(10),
            email: format!("{}@example.com", random_string(5)),
        })
        .collect()
}

fn generate_orders(
    customers: &[Customer],
    min_orders: usize,
    max_orders: usize,
    statuses: &[&str],
    random_status: bool,
) -> Vec<Order> {
    let products = vec!["Product A", "Product B", "Product C", "Product D"];
    let mut orders = Vec::new();
    let mut order_id = 1;

    for customer in customers {
        let num_orders = thread_rng().gen_range(min_orders..=max_orders);
        for j in 0..num_orders {
            let status = if random_status {
                statuses.choose(&mut thread_rng()).unwrap().to_string()
            } else {
                statuses[j % statuses.len()].to_string()
            };
            let order_date = chrono::Utc::now()
                .checked_sub_signed(chrono::Duration::days(thread_rng().gen_range(0..=365)))
                .unwrap()
                .format("%Y-%m-%d")
                .to_string();

            orders.push(Order {
                id: order_id,
                customer_id: customer.id,
                product_name: products.choose(&mut thread_rng()).unwrap().to_string(),
                quantity: thread_rng().gen_range(1..=10),
                order_date,
                status,
            });
            order_id += 1;
        }
    }
    orders
}

fn write_csv<P: AsRef<Path>>(filename: P, data: &[Vec<String>]) -> io::Result<()> {
    let file = File::create(filename)?;
    let mut writer = csv::Writer::from_writer(file);

    for record in data {
        writer.write_record(record)?;
    }
    writer.flush()?;
    Ok(())
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let num_customers: usize = args.get(1).and_then(|s| s.parse().ok()).unwrap_or(10);
    let min_orders: usize = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(5);
    let max_orders: usize = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(10);
    let statuses: Vec<&str> = args.get(4).map_or("Pending,Processing,Shipped,Delivered".to_string(), |s| s.to_string()).split(',').collect();
    let random_status: bool = args.get(5).and_then(|s| s.parse().ok()).unwrap_or(true);

    let customers = generate_customers(num_customers);
    let orders = generate_orders(&customers, min_orders, max_orders, &statuses, random_status);

    let customer_csv: Vec<Vec<String>> = std::iter::once(vec!["customer_id".to_string(), "customer_name".to_string(), "email".to_string()])
        .chain(customers.iter().map(|c| vec![c.id.to_string(), c.name.clone(), c.email.clone()]))
        .collect();
    write_csv("customers.csv", &customer_csv)?;

    let order_csv: Vec<Vec<String>> = std::iter::once(vec!["order_id".to_string(), "customer_id".to_string(), "product_name".to_string(), "quantity".to_string(), "order_date".to_string(), "status".to_string()])
        .chain(orders.iter().map(|o| vec![o.id.to_string(), o.customer_id.to_string(), o.product_name.clone(), o.quantity.to_string(), o.order_date.clone(), o.status.clone()]))
        .collect();
    write_csv("orders.csv", &order_csv)?;

    println!("顧客マスタデータと注文データがCSVファイルとして保存されました。");

    Ok(())
}
```

### 2. Cargoファイル (`Cargo.toml`)

以下のコードを `Cargo.toml` に保存します。

```toml
[package]
name = "data_generation"
version = "0.1.0"
edition = "2018"

[dependencies]
rand = "0.8"
chrono = "0.4"
csv = "1.1"

[dev-dependencies]
tempfile = "3.2"
```

### 3. テストコード (`main_test.rs`)

以下のコードを `tests/main_test.rs` に保存します。

```rust
use std::fs::File;
use std::io::{self, Read};
use tempfile::tempdir;

use data_generation::{generate_customers, generate_orders, write_csv};

#[test]
fn test_generate_customers() {
    let num_customers = 10;
    let customers = generate_customers(num_customers);
    assert_eq!(customers.len(), num_customers);
    for (i, customer) in customers.iter().enumerate() {
        assert_eq!(customer.id, i + 1);
        assert!(!customer.name.is_empty());
        assert!(customer.email.ends_with("@example.com"));
    }
}

#[test]
fn test_generate_orders() {
    let num_customers = 10;
    let min_orders = 5;
    let max_orders = 10;
    let customers = generate_customers(num_customers);
    let statuses = vec!["Pending", "Processing", "Shipped", "Delivered"];

    let orders = generate_orders(&customers, min_orders, max_orders, &statuses, true);
    assert!(orders.len() >= num_customers * min_orders);
    assert!(orders.len() <= num_customers * max_orders);

    let valid_statuses: Vec<String> = statuses.into_iter().map(|s| s.to_string()).collect();
    for (i, order) in orders.iter().enumerate() {
        assert_eq!(order.id, i + 1);
        assert!(order.customer_id >= 1 && order.customer_id <= num_customers);
        assert!(!order.product_name.is_empty());
        assert!(order.quantity >= 1 && order.quantity <= 10);
        assert!(valid_statuses.contains(&order.status));
    }

    let orders = generate_orders(&customers, min_orders, max_orders, &valid_statuses, false);
    for (i, order) in orders.iter().enumerate() {
        assert_eq!(order.status, valid_statuses[i % valid_statuses.len()]);
    }
}

#[test]
fn test_write_csv() -> io::Result<()> {
    let data = vec![
        vec!["ID".to_string(), "Name".to_string()],
        vec!["1".to_string(), "Alice".to_string()],
        vec!["2".to_string(), "Bob".to_string()],
    ];
    let dir = tempdir()?;
    let file_path = dir.path().join("test.csv");
    write_csv(&file_path, &data)?;

    let mut file = File::open(file_path)?;
    let mut contents = String::new();
    file.read_to_string(&mut contents)?;
    let expected = "ID,Name\n1,Alice\n2,Bob\n";
    assert_eq!(contents, expected);

    dir.close()?;
    Ok(())
}
```

### 実行手順

#### 1. プロジェクトの初期化

ターミナルを開き、プロジェクトディレクトリに移動して以下のコマンドを実行し、Cargoプロジェクトを初期化します。

```sh
cargo new data_generation
cd data_generation
```

次に、上記のコードをそれぞれのファイルにコピーし、保存します。

#### 2. プログラムの実行

ターミナルで以下のコマンドを実行してプログラムを実行します。

```sh
cargo run -- 10 5 10 "Pending,Processing,Shipped,Delivered" true
```

この例では、10人の顧客データと各顧客に対する5から10のランダムな注文数を生成し、注文ステータスをランダムに付与します。

注文ステータスを指定した順に付与したい場合は、`true`を`false`に変更します。

```sh
cargo run -- 10 5 10 "Pending,Processing,Shipped,Delivered" false
```

ステータスオプションを指定しない場合は、デフォルトのステータスが使用されます。

```sh
cargo run -- 10 5 10
```

#### 3. 生成されたCSVファイルの

確認

プログラムの実行が成功すると、以下の2つのCSVファイルが生成されます。

- `customers.csv`: 顧客データを含むファイル
- `orders.csv`: 注文データを含むファイル

これらのファイルを開いて、生成されたデータを確認します。

#### 4. テストの実行

ターミナルで以下のコマンドを実行して、プログラムのテストを実行します。

```sh
cargo test
```
