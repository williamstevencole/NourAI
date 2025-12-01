# Sistema de Evaluación RAG - Nutri-RAG MVP

Sistema completo de evaluación para el MVP de Nutri-RAG utilizando **RAGAS**, el framework estándar de la industria para evaluar sistemas RAG.

## 📋 Descripción

Este sistema evalúa el rendimiento del RAG en tres dimensiones:

### 1. **Métricas de Recuperación (Retrieval)**

- **Context Precision**: ¿Los contextos relevantes están en top positions?
- **Context Recall**: ¿Se recuperaron todos los contextos necesarios?
- **Precision@k**: Proporción de docs relevantes recuperados
- **Recall@k**: Cobertura de docs relevantes

### 2. **Métricas de Generación**

- **Faithfulness** (RAGAS): ¿La respuesta está basada en el contexto sin inventar?
- **Answer Relevancy** (RAGAS): ¿La respuesta es relevante a la pregunta?
- **Answer Correctness** (RAGAS): Precisión factual vs ground truth
- **BLEU**: Solapamiento de n-gramas (BLEU-1, BLEU-2, BLEU-3, BLEU-4)
- **ROUGE**: Similitud de texto (ROUGE-1, ROUGE-2, ROUGE-L)

### 3. **Métricas de Sistema**

- **Coverage**: % de consultas respondidas exitosamente
- **Latency**: Tiempo promedio de respuesta

---

## 🚀 Instalación

### 1. Instalar dependencias

Asegúrate de estar en el entorno virtual:

```bash
cd backend
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

Instalar RAGAS y dependencias:

```bash
pip install -r requirements.txt
```

### 2. Configurar OpenAI API Key

Este sistema usa **OpenAI** para las métricas RAGAS (más confiable y rápido).

```bash
# Configura tu API key de OpenAI
export OPENAI_API_KEY='tu-api-key-aqui'
```

**Ventajas de usar OpenAI:**

- ✅ Muy rápido (2-5 minutos para 5 casos)
- ✅ Resultados confiables y precisos
- ✅ Sin timeouts ni problemas de rendimiento
- ✅ Costo bajo (~$0.10-0.30 USD por 5 casos)

**Obtener API Key:**

1. Ve a https://platform.openai.com/api-keys
2. Crea una cuenta (incluye $5 de crédito gratis)
3. Genera una nueva API key
4. Configúrala como variable de entorno

---

## 📊 Dataset de Evaluación

El archivo `dataset.json` contiene 5 casos de prueba cuidadosamente diseñados:

1. **Diabetes Tipo 2**: Alimentos a evitar
2. **Hipertensión**: Consumo de sodio recomendado
3. **Plan Alimenticio**: Dieta semanal personalizada
4. **Nutrición Infantil**: Nutrientes esenciales
5. **Prevención**: Cambios en estilo de vida

Cada caso incluye:

- `query`: Pregunta de evaluación
- `expected_answer`: Respuesta esperada (ground truth)
- `relevant_docs`: IDs de documentos relevantes
- `clinical_data`: Datos del paciente (opcional)
- `category`: Categoría de la pregunta
- `difficulty`: Nivel de dificultad

---

## 🔧 Uso

### Evaluación Básica

```bash
cd backend/evaluation
python evaluate_ragas.py
```

### Evaluación con Detalles (Verbose)

```bash
python evaluate_ragas.py --verbose
```

---

## 📊 Interpretación de Métricas RAGAS

Todas las métricas RAGAS están en escala **0-1** (0% - 100%):

| Puntaje       | Interpretación             |
| ------------- | -------------------------- |
| **≥ 0.7**     | ✅ Excelente               |
| **0.5 - 0.7** | ⚠️ Bueno (mejoras menores) |
| **< 0.5**     | ❌ Necesita mejora         |

### Métricas Clave:

**Faithfulness (Fidelidad)** 🎯

- **Qué evalúa**: ¿El sistema inventa información o se basa fielmente en los documentos?
- **Importancia**: CRÍTICA - detecta "alucinaciones"
- **Objetivo**: > 0.8

**Answer Relevancy (Relevancia)** 🔍

- **Qué evalúa**: ¿La respuesta responde exactamente lo preguntado?
- **Importancia**: ALTA - evita respuestas genéricas o fuera de tema
- **Objetivo**: > 0.7

**Context Recall (Recall)** 📚

- **Qué evalúa**: ¿Se recuperó toda la información necesaria?
- **Importancia**: ALTA - evita respuestas incompletas
- **Objetivo**: > 0.7

**Context Precision (Precisión)** 🎯

- **Qué evalúa**: ¿Los documentos relevantes están en top positions?
- **Importancia**: MEDIA - mejora eficiencia
- **Objetivo**: > 0.6

**Answer Correctness (Precisión)** ✓

- **Qué evalúa**: ¿La respuesta es factualmente correcta?
- **Importancia**: CRÍTICA - información médica debe ser precisa
- **Objetivo**: > 0.8

---

## 🛠️ Personalización

### Agregar Nuevos Casos de Prueba

Edita `dataset.json` y agrega un nuevo caso:

```json
{
  "id": "test_006",
  "query": "Tu pregunta aquí",
  "expected_answer": "Respuesta esperada",
  "relevant_docs": ["doc_id_1", "doc_id_2"],
  "clinical_data": null,
  "category": "categoria",
  "difficulty": "medium"
}
```

### Modificar Métricas Evaluadas

En `evaluate_ragas.py`, línea ~180, puedes cambiar las métricas:

```python
ragas_results = evaluate(
    ragas_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        # Agrega o quita métricas aquí
    ],
)
```

Métricas disponibles en RAGAS:

- `faithfulness`
- `answer_relevancy`
- `context_recall`
- `context_precision`
- `answer_correctness`
- `answer_similarity`
- `context_relevancy`

---

## ⚠️ Notas Importantes

### Tiempo de Ejecución

- **Evaluación del RAG**: 1-3 minutos (5 casos de prueba)
- **Evaluación RAGAS con OpenAI**: 2-5 minutos
- **Total**: ~3-8 minutos para evaluación completa

### Costos

- **OpenAI API**: ~$0.10-0.30 USD por 5 casos de prueba
- Incluye evaluación con GPT-4 mini (muy preciso)
- OpenAI da $5 de crédito gratis al crear cuenta

### Métricas Incluidas

**RAGAS (con OpenAI):**

- Faithfulness, Answer Relevancy, Context Recall, Context Precision, Answer Correctness

**Adicionales (librerías Python):**

- Precision@k, Recall@k (recuperación)
- BLEU-1, BLEU-2, BLEU-3, BLEU-4 (n-gramas)
- ROUGE-1, ROUGE-2, ROUGE-L (similitud)
- Latency, Coverage

---

## 📚 Recursos Adicionales

- [Documentación RAGAS](https://docs.ragas.io/)
- [Paper RAGAS](https://arxiv.org/abs/2309.15217)
- [GitHub RAGAS](https://github.com/explodinggradients/ragas)

---

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY no encontrada"

**Solución**: Configura la variable de entorno:

```bash
export OPENAI_API_KEY='tu-api-key-aqui'

# O agrégala a tu .bashrc/.zshrc para que persista:
echo 'export OPENAI_API_KEY="tu-api-key"' >> ~/.zshrc
```

### Error: "Rate limit exceeded"

**Solución**: Has superado el límite de la API de OpenAI. Espera un momento o verifica tu tier en OpenAI.

### Error: "Module 'ragas' not found"

**Solución**: Instala RAGAS:

```bash
pip install ragas
```

### Error: "ChromaDB connection failed"

**Solución**: Verifica que la base de datos esté poblada:

```bash
cd backend/core
python populate_database.py
```

### Evaluación muy lenta

**Solución**:

- Reduce el número de casos de prueba
- Usa menos métricas RAGAS
- Usa modelo local más rápido

---

## 📞 Soporte

Para preguntas sobre:

- **RAGAS**: [GitHub Issues](https://github.com/explodinggradients/ragas/issues)
- **Este proyecto**: Contacta al equipo de desarrollo

---

_Sistema de evaluación desarrollado para Nutri-RAG MVP - 2025_
