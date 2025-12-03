# Instrucciones para la ejecucion del proyecto

## Terminal 1
```bash
cd backend
pip install -r requirements.txt

## Para re poblar la base de datos
python3 backend/core/populate_database.py --reset

python3 backend/api.py
```

## Terminal 2
```bash
cd frontend
npm i
npm run dev
```

## Terminal 3
```bash
ollama serve
```

## Terminal 4

```bash
ollama pull llama3.2:3b

ollama run llama3.2:3b
```

ctrl+d
ollama ps 
