package main

import (
	"encoding/csv"
	"os"
	"strconv"
	"strings"
	"testing"
	"time"
)

func TestGenerateCustomers(t *testing.T) {
	numCustomers := 10
	customers := generateCustomers(numCustomers)

	if len(customers) != numCustomers {
		t.Errorf("Expected %d customers, got %d", numCustomers, len(customers))
	}

	for i, customer := range customers {
		if customer.ID != i+1 {
			t.Errorf("Expected customer ID %d, got %d", i+1, customer.ID)
		}
		if len(customer.Name) == 0 {
			t.Errorf("Expected customer name to be non-empty")
		}
		if len(customer.Email) == 0 {
			t.Errorf("Expected customer email to be non-empty")
		}
	}
}

func TestGenerateOrders(t *testing.T) {
	numCustomers := 10
	minOrders := 5
	maxOrders := 10
	customers := generateCustomers(numCustomers)
	statusList := []string{"Pending", "Processing", "Shipped", "Delivered"}

	orders := generateOrders(customers, minOrders, maxOrders, statusList, true)
	if len(orders) < numCustomers*minOrders || len(orders) > numCustomers*maxOrders {
		t.Errorf("Expected number of orders between %d and %d, got %d", numCustomers*minOrders, numCustomers*maxOrders, len(orders))
	}

	statuses := map[string]bool{"Pending": true, "Processing": true, "Shipped": true, "Delivered": true}
	for i, order := range orders {
		if order.ID != i+1 {
			t.Errorf("Expected order ID %d, got %d", i+1, order.ID)
		}
		if order.CustomerID < 1 || order.CustomerID > numCustomers {
			t.Errorf("Order customer ID %d out of range", order.CustomerID)
		}
		if len(order.ProductName) == 0 {
			t.Errorf("Expected product name to be non-empty")
		}
		if order.Quantity < 1 || order.Quantity > 9 {
			t.Errorf("Order quantity %d out of range", order.Quantity)
		}
		if _, err := time.Parse("2006-01-02", order.OrderDate); err != nil {
			t.Errorf("Order date %s is not a valid date", order.OrderDate)
		}
		if !statuses[order.Status] {
			t.Errorf("Invalid order status %s", order.Status)
		}
	}

	orders = generateOrders(customers, minOrders, maxOrders, statusList, false)
	for i, order := range orders {
		if order.Status != statusList[i%len(statusList)] {
			t.Errorf("Expected order status %s, got %s", statusList[i%len(statusList)], order.Status)
		}
	}
}

func TestWriteCSV(t *testing.T) {
	data := [][]string{
		{"ID", "Name"},
		{"1", "Alice"},
		{"2", "Bob"},
	}

	filename := "test.csv"
	err := writeCSV(filename, data)
	if err != nil {
		t.Fatalf("Expected no error, got %v", err)
	}
	defer os.Remove(filename)

	file, err := os.Open(filename)
	if err != nil {
		t.Fatalf("Expected no error opening file, got %v", err)
	}
	defer file.Close()

	reader := csv.NewReader(file)
	records, err := reader.ReadAll()
	if err != nil {
		t.Fatalf("Expected no error reading file, got %v", err)
	}

	if len(records) != len(data) {
		t.Errorf("Expected %d records, got %d", len(data), len(records))
	}

	for i, record := range records {
		for j, field := range record {
			if field != data[i][j] {
				t.Errorf("Expected %s, got %s", data[i][j], field)
			}
		}
	}
}
