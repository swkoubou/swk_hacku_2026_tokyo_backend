#!/bin/sh
echo "Building server..."
cd ./api
go mod tidy
go build -o server .
tail -f /dev/null #デバッグ用
echo "Running server..."
./server

ls -la

echo "Server stopped"