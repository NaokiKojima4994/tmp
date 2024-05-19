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