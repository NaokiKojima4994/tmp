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