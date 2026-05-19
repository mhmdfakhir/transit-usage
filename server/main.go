package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/mhmdfakhir/transit-usage/handlers"
)

func main() {
	// Register our two endpoints
	http.HandleFunc("/upload", handlers.UploadHandler)
	http.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "ok")
	})

	port := ":8080"
	log.Printf("Server starting on http://localhost%s", port)

	// Start listening for requests — this line blocks forever (that's intentional)
	if err := http.ListenAndServe(port, nil); err != nil {
		log.Fatalf("Server failed to start: %v", err)
	}
}