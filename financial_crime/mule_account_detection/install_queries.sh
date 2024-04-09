#!/bin/bash

# Define the graph name
GRAPH_NAME="Mule_Account_Detection"

# Directory containing your .gsql files
QUERY_DIR="./queries"

# Iterate over each .gsql file in the directory
for file in "$QUERY_DIR"/*.gsql; do
    echo "Running $file..."
    gsql -g "$GRAPH_NAME" "$file"
done

echo "All scripts have been executed."

gsql --graph "$GRAPH_NAME" INSTALL QUERY ALL

