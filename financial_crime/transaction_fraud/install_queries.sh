#!/bin/bash

# Define the graph name
GRAPH_NAME="Transaction_Fraud"

# Directory containing your .gsql files
QUERY_DIR="./queries"

# Iterate over each .gsql file in the directory
for file in "$QUERY_DIR"/*.gsql; do
# Execute each query in the file
    # skip install_query.gsql
    if [ $file != "./queries/install_query.gsql" ]; then 
        echo "Running $file..."
        gsql -g "$GRAPH_NAME" "$file"
    fi
done

echo "All scripts have been executed."

gsql --graph "$GRAPH_NAME" INSTALL QUERY ALL

