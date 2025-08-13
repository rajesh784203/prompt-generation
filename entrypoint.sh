#!/bin/sh
# Start ollama in background
ollama serve &

# Wait for the API to be ready
sleep 8

# Pull the model
ollama pull deepseek-llm:7b

# Keep the server in the foreground
wait

