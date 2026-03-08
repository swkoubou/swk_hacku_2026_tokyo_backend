#!/bin/sh
echo "Building server..."
cd ./api
go mod tidy
go build -o server .

echo "Running server..."
./server

ls -la

echo "Server stopped"