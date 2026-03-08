package main

import (
	"context"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	openai "github.com/openai/openai-go/v3"
	"github.com/openai/openai-go/v3/option"
	"github.com/openai/openai-go/v3/responses"
	"github.com/joho/godotenv"
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
				Model: "gpt-5-mini", // 高速モデル
				Input: responses.ResponseNewParamsInputUnion{
					OfString: openai.String(message),
				},
			},
		)

		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		c.JSON(http.StatusOK, gin.H{
			"response": resp.OutputText(),
		})
	})

	log.Println("Server running on :8888")
	r.Run(":8888")
}