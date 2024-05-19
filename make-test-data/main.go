package main

import (
	"encoding/csv"
	"flag"
	"fmt"
	"math/rand"
	"os"
	"strconv"
	"strings"
	"time"
)

type Customer struct {
	ID    int
	Name  string
	Email string
}

type Order struct {
	ID         int
	CustomerID int
	ProductName string
	Quantity   int
	OrderDate  string
	Status     string
}

func randomString(n int) string {
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
	b := make([]byte, n)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

func generateCustomers(numCustomers int) []Customer {
	customers := make([]Customer, numCustomers)
	for i := 0; i < numCustomers; i++ {
		customers[i] = Customer{
			ID:    i + 1,
			Name:  randomString(10),
			Email: randomString(5) + "@example.com",
		}
	}
	return customers
}

func generateOrders(customers []Customer, minOrders, maxOrders int, statuses []string, randomStatus bool) []Order {
	rand.Seed(time.Now().UnixNano())
	products := []string{"Product A", "Product B", "Product C", "Product D"}
	orders := make([]Order, 0)
	orderID := 1

	for _, customer := range customers {
		numOrders := rand.Intn(maxOrders-minOrders+1) + minOrders
		for j := 0; j < numOrders; j++ {
			status := statuses[rand.Intn(len(statuses))]
			if !randomStatus {
				status = statuses[j%len(statuses)]
			}
			order := Order{
				ID:          orderID,
				CustomerID:  customer.ID,
				ProductName: products[rand.Intn(len(products))],
				Quantity:    rand.Intn(9) + 1,
				OrderDate:   time.Now().AddDate(0, 0, -rand.Intn(365)).Format("2006-01-02"),
				Status:      status,
			}
			orders = append(orders, order)
			orderID++
		}
	}

	return orders
}

func writeCSV(filename string, data [][]string) error {
	file, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()

	for _, record := range data {
		if err := writer.Write(record); err != nil {
			return err
		}
	}

	return nil
}

func main() {
	numCustomers := flag.Int("customers", 10, "Number of customers")
	minOrders := flag.Int("minOrders", 5, "Minimum number of orders per customer")
	maxOrders := flag.Int("maxOrders", 10, "Maximum number of orders per customer")
	statuses := flag.String("statuses", "", "Comma-separated list of order statuses")
	randomStatus := flag.Bool("randomStatus", true, "Assign statuses randomly")
	flag.Parse()

	// デフォルトステータスの設定
	if *statuses == "" {
		*statuses = "Pending,Processing,Shipped,Delivered"
	}

	customers := generateCustomers(*numCustomers)
	statusList := strings.Split(*statuses, ",")
	orders := generateOrders(customers, *minOrders, *maxOrders, statusList, *randomStatus)

	customerCSV := [][]string{
		{"customer_id", "customer_name", "email"},
	}
	for _, customer := range customers {
		customerCSV = append(customerCSV, []string{
			strconv.Itoa(customer.ID),
			customer.Name,
			customer.Email,
		})
	}

	orderCSV := [][]string{
		{"order_id", "customer_id", "product_name", "quantity", "order_date", "status"},
	}
	for _, order := range orders {
		orderCSV = append(orderCSV, []string{
			strconv.Itoa(order.ID),
			strconv.Itoa(order.CustomerID),
			order.ProductName,
			strconv.Itoa(order.Quantity),
			order.OrderDate,
			order.Status,
		})
	}

	if err := writeCSV("customers.csv", customerCSV); err != nil {
		fmt.Println("Error writing customers.csv:", err)
	}
	if err := writeCSV("orders.csv", orderCSV); err != nil {
		fmt.Println("Error writing orders.csv:", err)
	}

	fmt.Println("顧客マスタデータと注文データがCSVファイルとして保存されました。")
}