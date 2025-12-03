#!/bin/bash
# Initialize data directory with empty JSON files if they don't exist

mkdir -p service/data

# Create empty JSON files if they don't exist
for file in users.json profile.json meal_plans.json daily_logs.json; do
  if [ ! -f "service/data/$file" ]; then
    echo "{}" > "service/data/$file"
  fi
done

echo "Data directory initialized successfully"
