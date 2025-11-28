# Terminal 1
cd backend
pip install -r requirements.txt

# Para re poblar la base de datos
python3 backend/core/populate_database.py --reset

# Terminal 2
cd frontend
npm i
npm run dev

# Terminal 3

ollama pull llama3.2:3b

ollama run llama3.2:3b
ctrl+d
ollama ps 