#!/bin/bash

ollama stop deepseek-llm:7b
ollama rm deepseek-llm:7b

ollama ps
ollama list

sudo rm /usr/local/bin/ollama
rm -rf ~/.ollama

sudo systemctl disable ollama
sudo systemctl stop ollama
sudo rm /etc/systemd/system/ollama.service

