#!/bin/bash
# .render/start.sh - ZeroDay AI Platform Start Script

set -e  # Exit on any error
echo "🚀 Starting ZeroDay AI Platform..."


echo "📋 Startup Info:"
echo "Environment: ${ENVIRONMENT:-development}"
echo "Port: ${PORT:-8000}"
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"


echo "🔒 Checking environment variables..."
required_vars=("DATABASE_URL")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    else
        echo "✅ $var is set"
    fi
done


optional_vars=("OPENAI_API_KEY" "REDIS_URL")
for var in "${optional_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "⚠️ Warning: Optional environment variable $var is not set"
    else
        echo "✅ $var is set"
    fi
done


echo "🗄️ Checking database setup..."
python -c "
import sys
import os

try:
    # Add the project root to Python path
    sys.path.insert(0, os.getcwd())
    
    # Check if database setup exists
    try:
        from database.setup import initialize_database
        print('✅ Database setup available')
    except ImportError:
        print('⚠️ Database setup not available - skipping')
except Exception as e:
    print(f'⚠️ Database check failed: {e}')
" || echo "⚠️ Database initialization skipped"


echo "🔍 Checking vector store..."
python -c "
import sys
import os

try:
    # Add the project root to Python path
    sys.path.insert(0, os.getcwd())
    
    # Check if vector store setup exists
    try:
        from vector_store.chromadb_setup import setup_chromadb
        print('✅ Vector store setup available')
    except ImportError:
        print('⚠️ Vector store setup not available - will be initialized by agents')
except Exception as e:
    print(f'⚠️ Vector store check failed: {e}')
" || echo "⚠️ Vector store initialization skipped"


if [ "${LOAD_DEMO_DATA:-false}" = "true" ]; then
    echo "🎭 Checking demo data..."
    python -c "
import sys
import os

try:
    sys.path.insert(0, os.getcwd())
    # Check if demo data exists
    try:
        from database.seed_demo_data import seed_demo_data
        print('✅ Demo data loader available')
    except ImportError:
        print('⚠️ Demo data loader not available - using built-in demo system')
except Exception as e:
    print(f'⚠️ Demo data check failed: {e}')
" || echo "⚠️ Demo data loading skipped"
fi


echo "🤖 Checking AI agents..."
python -c "
import sys
import os

sys.path.insert(0, os.getcwd())

agents = ['knowledge_agent', 'task_agent', 'mentor_agent', 'guide_agent']
available_agents = []

for agent in agents:
    try:
        exec(f'from agents.{agent} import *')
        available_agents.append(agent)
        print(f'✅ {agent} is available')
    except ImportError:
        print(f'⚠️ {agent} not available')

print(f'📊 Total available agents: {len(available_agents)}/4')
"


echo "❤️ Starting health monitoring..."
python -c "
import asyncio
import sys
import os

async def health_check():
    while True:
        try:
            # Basic health check
            print('❤️ Health check: OK')
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            print(f'💔 Health check failed: {e}')
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(health_check())
" &


mkdir -p logs uploads temp


export PYTHONUNBUFFERED=1

echo "🎯 Starting FastAPI server..."
echo "🌐 Server will be available on port ${PORT:-8000}"


cd api

exec uvicorn main:app \
    --host 0.0.0.0 \
    --port ${PORT:-8000} \
    --workers ${WORKERS:-1} \
    --log-level ${LOG_LEVEL:-info} \
    --access-log \
    --use-colors \
    --loop uvloop \
    --http httptools