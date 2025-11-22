#!/bin/bash

# OCR Research Runner Script
# Quick access to research tools

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=========================================="
echo "🔬 OCR RESEARCH TOOLS"
echo "=========================================="
echo ""
echo "Select option:"
echo "1. Batch process all datasets (Direct)"
echo "2. Batch process via API"
echo "3. Test single image"
echo "4. View latest CSV results"
echo "5. Analyze CSV results"
echo "6. Count images per category"
echo "7. Exit"
echo ""
read -p "Enter choice [1-7]: " choice

case $choice in
    1)
        echo ""
        echo "🚀 Running batch processing (Direct)..."
        cd "$PROJECT_DIR"
        python research/batch_process_datasets.py
        ;;
    2)
        echo ""
        echo "🌐 Running batch processing (API)..."
        echo "⚠️  Make sure API server is running!"
        read -p "Press Enter to continue or Ctrl+C to cancel..."
        cd "$PROJECT_DIR"
        python research/batch_process_via_api.py
        ;;
    3)
        echo ""
        read -p "Enter image path: " img_path
        read -p "Enter category (optional): " category
        cd "$PROJECT_DIR"
        if [ -z "$category" ]; then
            python research/test_single_image.py "$img_path"
        else
            python research/test_single_image.py "$img_path" "$category"
        fi
        ;;
    4)
        echo ""
        echo "📊 Latest CSV results:"
        cd "$SCRIPT_DIR"
        latest_csv=$(ls -t ocr_validation_*.csv 2>/dev/null | head -1)
        if [ -z "$latest_csv" ]; then
            echo "❌ No CSV files found"
        else
            echo "📁 File: $latest_csv"
            echo ""
            head -20 "$latest_csv"
            echo ""
            echo "... (showing first 20 lines)"
        fi
        ;;
    5)
        echo ""
        echo "📊 Analyzing CSV results..."
        cd "$SCRIPT_DIR"
        python analyze_results.py
        ;;
    6)
        echo ""
        echo "📊 Images per category:"
        echo "----------------------------------------"
        cd "$PROJECT_DIR/datasets"
        for dir in */; do
            count=$(find "$dir" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)
            printf "%-25s: %d images\n" "${dir%/}" "$count"
        done
        echo "----------------------------------------"
        total=$(find . -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)
        echo "Total: $total images"
        ;;
    7)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "✅ Done!"
