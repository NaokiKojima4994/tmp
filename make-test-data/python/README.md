# データ生成プログラム

このプログラムは、指定された顧客数と各顧客に紐づく注文数を生成し、CSVファイルとして保存します。

## 必要な準備

1. [Python](https://www.python.org/downloads/)がインストールされていることを確認してください。
2. プロジェクトのディレクトリを作成し、そこにプログラムファイルを保存します。

## プログラムファイルの準備

### 1. メインプログラム (`main.py`)

以下のコードを `main.py` というファイル名で保存してください。

```python
import csv
import random
import string
import argparse
from datetime import datetime, timedelta

def random_string(n):
    return ''.join(random.choices(string.ascii_letters, k=n))

def generate_customers(num_customers):
    customers = []
    for i in range(1, num_customers + 1):
        customers.append({
            'customer_id': i,
            'customer_name': random_string(10),
            'email': random_string(5) + "@example.com"
        })
    return customers

def generate_orders(customers, min_orders, max_orders, statuses, random_status):
    products = ['Product A', 'Product B', 'Product C', 'Product D']
    orders = []
    order_id = 1

    for customer in customers:
        num_orders = random.randint(min_orders, max_orders)
        for j in range(num_orders):
            status = random.choice(statuses) if random_status else statuses[j % len(statuses)]
            order_date = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d')
            orders.append({
                'order_id': order_id,
                'customer_id': customer['customer_id'],
                'product_name': random.choice(products),
                'quantity': random.randint(1, 10),
                'order_date': order_date,
                'status': status
            })
            order_id += 1

    return orders

def write_csv(filename, data, headers):
    with open(filename, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

def main():
    parser = argparse.ArgumentParser(description='Generate customer and order data.')
    parser.add_argument('-c', '--customers', type=int, default=10, help='Number of customers')
    parser.add_argument('-min', '--minOrders', type=int, default=5, help='Minimum number of orders per customer')
    parser.add_argument('-max', '--maxOrders', type=int, default=10, help='Maximum number of orders per customer')
    parser.add_argument('-s', '--statuses', default="Pending,Processing,Shipped,Delivered", help='Comma-separated list of order statuses')
    parser.add_argument('-r', '--randomStatus', type=bool, default=True, help='Assign statuses randomly')
    args = parser.parse_args()

    customers = generate_customers(args.customers)
    status_list = args.statuses.split(',')
    orders = generate_orders(customers, args.minOrders, args.maxOrders, status_list, args.randomStatus)

    write_csv('customers.csv', customers, ['customer_id', 'customer_name', 'email'])
    write_csv('orders.csv', orders, ['order_id', 'customer_id', 'product_name', 'quantity', 'order_date', 'status'])

    print("顧客マスタデータと注文データがCSVファイルとして保存されました。")

if __name__ == '__main__':
    main()
```

### 2. テストプログラム (`test_main.py`)

以下のコードを `test_main.py` というファイル名で保存してください。

```python
import unittest
import os
from main import generate_customers, generate_orders, write_csv

class TestDataGeneration(unittest.TestCase):

    def test_generate_customers(self):
        num_customers = 10
        customers = generate_customers(num_customers)
        self.assertEqual(len(customers), num_customers)
        for i, customer in enumerate(customers):
            self.assertEqual(customer['customer_id'], i + 1)
            self.assertTrue(len(customer['customer_name']) > 0)
            self.assertTrue(len(customer['email']) > 0)

    def test_generate_orders(self):
        num_customers = 10
        min_orders = 5
        max_orders = 10
        customers = generate_customers(num_customers)
        statuses = ["Pending", "Processing", "Shipped", "Delivered"]

        orders = generate_orders(customers, min_orders, max_orders, statuses, True)
        self.assertGreaterEqual(len(orders), num_customers * min_orders)
        self.assertLessEqual(len(orders), num_customers * max_orders)

        valid_statuses = set(statuses)
        for i, order in enumerate(orders):
            self.assertEqual(order['order_id'], i + 1)
            self.assertIn(order['customer_id'], range(1, num_customers + 1))
            self.assertTrue(len(order['product_name']) > 0)
            self.assertIn(order['quantity'], range(1, 11))
            self.assertIn(order['status'], valid_statuses)

        orders = generate_orders(customers, min_orders, max_orders, statuses, False)
        for i, order in enumerate(orders):
            self.assertEqual(order['status'], statuses[i % len(statuses)])

    def test_write_csv(self):
        data = [
            {'ID': 1, 'Name': 'Alice'},
            {'ID': 2, 'Name': 'Bob'}
        ]
        filename = 'test.csv'
        headers = ['ID', 'Name']
        write_csv(filename, data, headers)
        self.assertTrue(os.path.exists(filename))

        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
            self.assertEqual(len(rows), len(data))
            for row, item in zip(rows, data):
                self.assertEqual(int(row['ID']), item['ID'])
                self.assertEqual(row['Name'], item['Name'])

        os.remove(filename)

if __name__ == '__main__':
    unittest.main()
```

## 実行手順

### 1. プログラムの実行

ターミナルを開き、プログラムが保存されたディレクトリに移動します。以下のコマンドを実行してプログラムを実行します。

```sh
python main.py -c 10 -min 5 -max 10 -s "Pending,Processing,Shipped,Delivered" -r True
```

この例では、10人の顧客データと各顧客に対する5から10のランダムな注文数を生成し、注文ステータスをランダムに付与します。

注文ステータスを指定した順に付与したい場合は、`-r`を`False`に設定します。

```sh
python main.py -c 10 -min 5 -max 10 -s "Pending,Processing,Shipped,Delivered" -r False
```

ステータスオプションを指定しない場合は、デフォルトのステータスが使用されます。

```sh
python main.py -c 10 -min 5 -max 10 -r True
```

### 2. 生成されたCSVファイルの確認

プログラムの実行が成功すると、以下の2つのCSVファイルが生成されます。

- `customers.csv`: 顧客データを含むファイル
- `orders.csv`: 注文データを含むファイル

これらのファイルを開いて、生成されたデータを確認します。

### 3. テストの実行

ターミナルで以下のコマンドを実行して、プログラムのテストを実行します。

```sh
python -m unittest discover
```

このコマンドにより、テストが実行され、結果が表示されます。すべてのテストが成功すると、プログラムが正しく実装されていることが確認できます。