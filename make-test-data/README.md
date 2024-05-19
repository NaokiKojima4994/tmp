### メインプログラム (`main.go`)

```go
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
```

### テストプログラム (`main_test.go`)

以下のコードを `main_test.go` というファイル名で保存してください。

```go
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
```

## 実行手順

### 1. プログラムのビルドと実行

ターミナルを開き、プログラムが保存されたディレクトリに移動します。以下のコマンドを実行してプログラムを実行します。

```sh
go run main.go -customers 10 -minOrders 5 -maxOrders 10 -statuses "Pending,Processing,Shipped,Delivered" -randomStatus true
```

この例では、10人の顧客データと各顧客に対する5から10のランダムな注文数

を生成し、注文ステータスをランダムに付与します。

注文ステータスを指定した順に付与したい場合は、`-randomStatus`を`false`に設定します。

```sh
go run main.go -customers 10 -minOrders 5 -maxOrders 10 -statuses "Pending,Processing,Shipped,Delivered" -randomStatus false
```

ステータスオプションを指定しない場合は、デフォルトのステータスが使用されます。

```sh
go run main.go -customers 10 -minOrders 5 -maxOrders 10 -randomStatus true
```

### 2. 生成されたCSVファイルの確認

プログラムの実行が成功すると、以下の2つのCSVファイルが生成されます。

- `customers.csv`: 顧客データを含むファイル
- `orders.csv`: 注文データを含むファイル

これらのファイルを開いて、生成されたデータを確認します。

### 3. テストの実行

ターミナルで以下のコマンドを実行して、プログラムのテストを実行します。

```sh
go test -v
```

このコマンドにより、テストが実行され、結果が表示されます。すべてのテストが成功すると、プログラムが正しく実装されていることが確認できます。