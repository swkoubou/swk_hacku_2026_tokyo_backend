package main

import (
	"context"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	openai "github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/option"
	"github.com/openai/openai-go/v3/responses"
)

func main() {
	r := gin.Default()

	// ../.env から読み込む場合
	err := godotenv.Load("../.env")
	if err != nil {
		log.Println("Warning: .env file not found, using system environment")
	}

	apiKey := os.Getenv("OPENAI_API_KEY")
	if apiKey == "" {
		log.Fatal("OPENAI_API_KEY is not set")
	}

	// APIキーをセット
	client := openai.NewClient(
		option.WithAPIKey(apiKey),
	)

	r.GET("/chat", func(c *gin.Context) {
		message := c.Query("message")
		if message == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "message is required"})
			return
		}

		resp, err := client.Responses.New(
			context.Background(),
			responses.ResponseNewParams{
				Model: openai.ChatModelGPT4_1Nano, // 高速モデル 4.1nanoが最速！
				Input: responses.ResponseNewParamsInputUnion{
					OfString: openai.String(`
					レスポンスは必ずJSONで返してください。
					あなたは会話から得られた情報を元に、適切な返答を生成してください。
					以下がサンプルです
					{
						"start_date": "2026-03-09",
						"start_time": "10:40:00",
						"end_date": "2026-03-10",
						"event_name": "旅行"
					}
					"start_time"は必ずHH:MM:00の形式で返してください。
					秒数の情報はひつようありませんので
					また、n時などの明確な時間の指定がされてない場合はNULLを返してください。
					以下がNULLを返すサンプルです
					{
						"start_date": "2026-03-09",
						"start_time": null,
						"end_date": "2026-03-10",
						"event_name": "旅行"
					}
					開始日と終了日が不明な場合は本日の日付を使用してください。
					それでは入力をはじめます。
					` + message),
				},
			},
		)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"process_lv": 2,
			"response":   resp.OutputText(),
		})
	})

	log.Println("Server running on :8888")
	r.Run(":8888")
}
