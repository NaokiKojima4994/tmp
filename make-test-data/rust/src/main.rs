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
