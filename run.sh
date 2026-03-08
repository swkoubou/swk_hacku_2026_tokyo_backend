#!/bin/sh
echo "Building server..."
go build -o server .

echo "Running server..."
./server

echo "Server stopped"