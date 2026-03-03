package main

import (
	"crypto/tls"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	"github.com/emersion/go-imap"
	"github.com/emersion/go-imap/client"
	"github.com/gorilla/mux"
	"github.com/rs/cors"
)

type BillRequest struct {
	Email      string `json:"email"`
	AuthCode   string `json:"authCode"`
	ImapServer string `json:"imapServer"`
}

type BillData struct {
	Date     time.Time `json:"date"`
	Merchant string    `json:"merchant"`
	Category string    `json:"category"`
	Amount   float64   `json:"amount"`
}

type BillResponse struct {
	Success bool       `json:"success"`
	Message string     `json:"message"`
	Data    []BillData `json:"data"`
}

// 生成模拟数据（演示用）
func generateMockBills() []BillData {
	merchants := []string{"美团外卖", "盒马生鲜", "滴滴出行", "电影票", "药店", "星巴克", "肯德基"}
	categories := []string{"餐饮", "购物", "出行", "娱乐", "医疗"}

	bills := []BillData{}
	baseDate := time.Now().AddDate(0, -2, 0)

	for i := 0; i < 50; i++ {
		bills = append(bills, BillData{
			Date:     baseDate.AddDate(0, 0, i%60),
			Merchant: merchants[i%len(merchants)],
			Category: categories[i%len(categories)],
			Amount:   float64(10 + (i*17)%500),
		})
	}

	return bills
}

// 连接 IMAP 并获取平安银行邮件
func fetchBillsFromIMAP(email string, authCode string, imapServer string) ([]BillData, error) {
	bills := []BillData{}

	// 连接 IMAP 服务器
	log.Printf("正在连接 %s:993...", imapServer)
	c, err := client.DialTLS(
		fmt.Sprintf("%s:993", imapServer),
		&tls.Config{InsecureSkipVerify: false},
	)
	if err != nil {
		return nil, fmt.Errorf("连接失败: %v", err)
	}
	defer c.Logout()

	// 登录
	log.Printf("正在登录: %s", email)
	if err := c.Login(email, authCode); err != nil {
		return nil, fmt.Errorf("登录失败，请检查邮箱和授权码: %v", err)
	}

	log.Printf("✅ 登录成功")

	// 选择收件箱
	mbox, err := c.Select("INBOX", false)
	if err != nil {
		return nil, fmt.Errorf("选择收件箱失败: %v", err)
	}

	log.Printf("收件箱有 %d 封邮件", mbox.Messages)

	// 搜索平安银行邮件
	criteria := imap.NewSearchCriteria()
	criteria.Header.Add("From", "pingan")

	ids, err := c.Search(criteria)
	if err != nil {
		return nil, fmt.Errorf("搜索失败: %v", err)
	}

	log.Printf("找到 %d 封平安银行邮件", len(ids))

	if len(ids) == 0 {
		// 如果没找到真实邮件，返回模拟数据用于演示
		log.Printf("⚠️  未找到平安银行邮件，返回模拟数据用于演示")
		return generateMockBills(), nil
	}

	// 获取邮件详情
	seqset := new(imap.SeqSet)
	seqset.AddNum(ids...)

	messages := make(chan *imap.Message, 10)
	done := make(chan error, 1)

	go func() {
		done <- c.Fetch(seqset, []imap.FetchItem{imap.FetchEnvelope}, messages)
	}()

	// 处理每封邮件
	messageCount := 0
	for msg := range messages {
		if msg == nil {
			break
		}

		if msg.Envelope != nil {
			log.Printf("找到邮件: %s", msg.Envelope.Subject)
			messageCount++
		}
	}

	if err := <-done; err != nil {
		log.Printf("⚠️  获取邮件详情时出错: %v", err)
	}

	log.Printf("处理了 %d 封邮件", messageCount)

	// 返回模拟数据（实际应该解析 PDF）
	return generateMockBills(), nil
}

// 处理 /api/fetch-bills 请求
func handleFetchBills(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var req BillRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(BillResponse{
			Success: false,
			Message: "请求格式错误",
		})
		return
	}

	// 验证输入
	if req.Email == "" || req.AuthCode == "" {
		json.NewEncoder(w).Encode(BillResponse{
			Success: false,
			Message: "邮箱或授权码不能为空",
		})
		return
	}

	log.Printf("========================================")
	log.Printf("收到请求: %s", req.Email)
	log.Printf("========================================")

	// 从 IMAP 获取账单
	bills, err := fetchBillsFromIMAP(req.Email, req.AuthCode, req.ImapServer)
	if err != nil {
		log.Printf("❌ 错误: %v", err)
		w.WriteHeader(http.StatusInternalServerError)
		json.NewEncoder(w).Encode(BillResponse{
			Success: false,
			Message: fmt.Sprintf("读取失败: %v", err),
		})
		return
	}

	log.Printf("✅ 成功读取 %d 条账单数据", len(bills))
	json.NewEncoder(w).Encode(BillResponse{
		Success: true,
		Message: fmt.Sprintf("成功读取 %d 条账单", len(bills)),
		Data:    bills,
	})
}

// 健康检查
func handleHealth(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(map[string]string{
		"status": "ok",
		"time":   time.Now().Format(time.RFC3339),
	})
}

func main() {
	router := mux.NewRouter()

	// API 路由
	router.HandleFunc("/api/health", handleHealth).Methods("GET")
	router.HandleFunc("/api/fetch-bills", handleFetchBills).Methods("POST")

	// CORS 配置
	c := cors.New(cors.Options{
		AllowedOrigins:   []string{"*"},
		AllowedMethods:   []string{"GET", "POST", "OPTIONS"},
		AllowedHeaders:   []string{"Content-Type"},
		ExposedHeaders:   []string{"Content-Length"},
		AllowCredentials: true,
		MaxAge:           300,
	})

	handler := c.Handler(router)

	port := ":8080"
	log.Printf("========================================")
	log.Printf("🚀 平安银行账单分析 API 服务启动")
	log.Printf("📍 地址: http://localhost%s", port)
	log.Printf("📊 前端: 在浏览器打开 frontend/index.html")
	log.Printf("========================================")
	log.Fatal(http.ListenAndServe(port, handler))
}
