# Terminal 1
cd backend

python3 backend/core/populate_database.py --reset

# Terminal 2
cd frontend
npm i
npm run dev

# Terminal 3
ollama run llama3.2:3b
ctrl+d
ollama ps 