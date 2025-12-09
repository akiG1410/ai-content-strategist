#!/bin/bash

# AI Content Marketing Strategist - Startup Script
# This script launches the Streamlit web application

echo "═══════════════════════════════════════════════════════════════"
echo "  🎯 AI Content Marketing Strategist - Starting Application"
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "   Please run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "   Creating template .env file..."
    cat > .env << 'EOF'
OPENROUTER_API_KEY=your_api_key_here
EOF
    echo "   ✅ Created .env file"
    echo "   ⚠️  Please edit .env and add your OPENROUTER_API_KEY"
    echo ""
    read -p "Press Enter to continue once you've added your API key..."
fi

# Check if outputs directory exists
if [ ! -d "outputs" ]; then
    echo "📁 Creating outputs directory..."
    mkdir -p outputs
    echo "   ✅ Created outputs directory"
fi

# Display startup info
echo "🚀 Starting Streamlit web application..."
echo ""
echo "📱 The app will open in your browser at:"
echo "   Local:    http://localhost:8501"
echo "   Network:  http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):8501"
echo ""
echo "💡 Tips:"
echo "   • Fill out the 8-step questionnaire"
echo "   • AI will generate 5 strategy options"
echo "   • Select one and generate a full content calendar"
echo "   • Download Word, Excel, and markdown files"
echo ""
echo "🛑 To stop the app, press Ctrl+C in this terminal"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Start Streamlit
./venv/bin/streamlit run src/streamlit_app.py --server.headless true --server.port 8501

# Cleanup message if stopped
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "  ✅ Application stopped successfully"
echo "═══════════════════════════════════════════════════════════════"
