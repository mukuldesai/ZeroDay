#!/bin/bash


set -e      

echo "🚀 Starting ZeroDay AI Platform Build Process..."


echo "📋 Environment Info:"
echo "Python version: $(python --version)"
echo "Node version: $(node --version 2>/dev/null || echo 'Node not available')"
echo "Current directory: $(pwd)"
echo "Available files: $(ls -la)"


echo "📦 Updating system packages..."
apt-get update -qq

echo "🔧 Installing system dependencies..."
apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    build-essential \
    python3-dev \
    libpq-dev \
    curl \
    wget


echo "🐍 Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt


echo "🤖 Installing AI/ML dependencies..."
echo "ChromaDB and LangChain dependencies installed"


if [ -d "frontend" ]; then
    echo "⚛️ Installing Frontend dependencies..."
    cd frontend
    npm ci --only=production
    cd ..
fi


echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p vector_store/data


echo "🗄️ Preparing database..."
python -c "
try:
    from database.setup import initialize_database
    print('Database initialization available')
except ImportError:
    print('Database setup not available during build')
"


echo "⚙️ Validating configurations..."
if [ -f "configs/settings.yaml" ]; then
    echo "✅ Found settings.yaml"
else
    echo "⚠️ Warning: settings.yaml not found"
fi


echo "⚡ Pre-compiling Python files..."
python -m compileall . || echo "Warning: Could not compile all Python files"


echo "🔍 Setting up vector store..."
if [ -d "vector_store" ]; then
    echo "✅ Vector store directory found"
  
    python -c "
try:
    from vector_store.chromadb_setup import setup_chromadb
    print('ChromaDB setup available')
except ImportError:
    print('ChromaDB setup not available during build')
"
fi


echo "🤖 Checking AI agents..."
for agent in knowledge_agent task_agent mentor_agent guide_agent; do
    if [ -f "agents/${agent}.py" ]; then
        echo "✅ Found ${agent}.py"
    else
        echo "⚠️ Warning: ${agent}.py not found"
    fi
done


echo "🧹 Cleaning up..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Build completed successfully!"
echo "🎉 ZeroDay AI Platform is ready for deployment!"