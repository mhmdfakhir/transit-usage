package handlers

import (
	// "encoding/json"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
)

func UploadHandler(w http.ResponseWriter, r *http.Request) {
	// Only allow POST requests
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	// Tell the browser it's allowed to talk to this server
	// (this is called CORS — needed because your frontend and
	// backend run on different ports during development)
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.Header().Set("Content-Type", "application/json")

	// Read the uploaded CSV file from the request
	// "file" is the field name the frontend will use when sending
	uploadedFile, _, err := r.FormFile("file")
	if err != nil {
		http.Error(w, "Could not read uploaded file", http.StatusBadRequest)
		return
	}
	defer uploadedFile.Close()

	// Save the uploaded file temporarily to disk so Python can read it
	tmpFile, err := os.CreateTemp("", "translink-*.csv")
	if err != nil {
		http.Error(w, "Could not create temp file", http.StatusInternalServerError)
		return
	}
	defer os.Remove(tmpFile.Name()) // clean up after we're done

	// Copy the uploaded bytes into the temp file
	buf := make([]byte, 1024*1024) // 1MB buffer
	for {
		n, err := uploadedFile.Read(buf)
		if n > 0 {
			tmpFile.Write(buf[:n])
		}
		if err != nil {
			break
		}
	}
	tmpFile.Close()

	// Work out where the Python pipeline folder is relative to this server
	pipelineDir, err := filepath.Abs("../pipeline")
	if err != nil {
		http.Error(w, "Could not locate pipeline", http.StatusInternalServerError)
		return
	}

	// Run the Python pipeline, passing the temp CSV path as an argument
	cmd := exec.Command("python", "run_pipeline.py", tmpFile.Name())
	cmd.Dir = pipelineDir

	output, err := cmd.Output()
	if err != nil {
		http.Error(w, "Pipeline failed: "+err.Error(), http.StatusInternalServerError)
		return
	}

	// The pipeline prints JSON to stdout — forward it straight to the frontend
	w.WriteHeader(http.StatusOK)
	w.Write(output)
}