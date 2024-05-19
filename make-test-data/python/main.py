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