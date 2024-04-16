#!/bin/bash

# Define the graph name
GRAPH_NAME="Transaction_Fraud"

# Directory containing your .gsql files
QUERY_DIR="./queries"

gsql -p "graphtiger" -g Transaction_Fraud ./queries/mer_shortest_path_length.gsql
gsql -p "graphtiger" -g Transaction_Fraud INSTALL QUERY mer_shortest_path_length

# Iterate over each .gsql file in the directory
for file in "$QUERY_DIR"/*.gsql; do
    # Skip the mer_shortest_path_length.gsql file and install_query.gsql file
    if [[ "$(basename "$file")" != "mer_shortest_path_length.gsql" &&  "$(basename "$file")" != "install_query.gsql" ]]; then
        echo "Running $file..."
        gsql -p "graphtiger" -g "$GRAPH_NAME" "$file"
    else
        echo "Skipping $file..."
    fi
done

echo "All scripts have been executed."

gsql -p "graphtiger" --graph "$GRAPH_NAME" INSTALL QUERY ALL

