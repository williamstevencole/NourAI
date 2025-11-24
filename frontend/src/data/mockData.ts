import { Message, Citation, QuickPrompt, ChatFilter } from "@/types/chat";

export const mockCitations: Citation[] = [
  {
    id: "fao-2022",
    label: "FAO 2022",
    organization: "FAO",
    year: "2022",
    title:
      "Guías alimentarias basadas en alimentos para la población hondureña",
    url: "https://www.fao.org/nutrition/education/food-based-dietary-guidelines",
    excerpt:
      "Las guías alimentarias recomiendan 5 porciones de frutas y verduras al día para una dieta equilibrada.",
  },
  {
    id: "ops-2023",
    label: "OPS 2023",
    organization: "OPS",
    year: "2023",
    title:
      "Prevención de enfermedades crónicas no transmisibles en Latinoamérica",
    url: "https://www.paho.org/es/temas/enfermedades-no-transmisibles",
    excerpt:
      "La reducción del consumo de sodio a menos de 2g/día puede prevenir enfermedades cardiovasculares.",
  },
  {
    id: "gaba-sesal",
    label: "GABA SESAL",
    organization: "SESAL",
    year: "2021",
    title: "Guías Alimentarias Basadas en Alimentos para Honduras",
    url: "https://www.salud.gob.hn",
    excerpt:
      "Las porciones recomendadas varían según la edad y actividad física del individuo.",
  },
];

export const mockMessages: Message[] = [
  {
    id: "1",
    role: "assistant",
    content: `¡Hola! Soy **NutriRAG**, tu asistente educativo de nutrición. Puedo ayudarte con:

- Información sobre **porciones** recomendadas según edad (GABA)
- Alimentos hondureños ricos en **nutrientes** específicos
- Consejos para **reducir sodio y azúcares** añadidos
- **Prevención** de enfermedades crónicas a través de la alimentación

Toda mi información proviene de fuentes oficiales como FAO, OPS y SESAL. ¿En qué puedo ayudarte hoy?`,
    timestamp: new Date(Date.now() - 1000 * 60 * 5),
  },
  {
    id: "2",
    role: "user",
    content:
      "¿Cuáles son las porciones recomendadas de verduras para un niño de 7 años?",
    timestamp: new Date(Date.now() - 1000 * 60 * 4),
  },
  {
    id: "3",
    role: "assistant",
    content: `Según las **Guías Alimentarias Basadas en Alimentos (GABA)** de Honduras, para niños de 7 años se recomienda:

### Porciones de Verduras
- **3-4 porciones** al día
- Cada porción equivale a:
  - 1 taza de verduras de hoja verde crudas
  - 1/2 taza de verduras cocidas
  - 1/2 taza de jugo de verduras 100% natural

### Recomendaciones Adicionales
1. **Variedad de colores**: Incluir verduras de diferentes colores (verde, naranja, rojo) para asegurar diversos nutrientes
2. **Preparación**: Preferir cocción al vapor o crudas para mantener vitaminas
3. **Combinaciones**: Integrar en platillos tradicionales hondureños como sopas o guisos

### Alimentos Locales Recomendados
- Güisquil (chayote)
- Pepino
- Tomate
- Zanahoria
- Hojas verdes (espinaca, acelga)

La **fibra** de las verduras ayuda a prevenir el estreñimiento y contribuye a un peso saludable.`,
    citations: [mockCitations[2], mockCitations[0]],
    timestamp: new Date(Date.now() - 1000 * 60 * 3),
  },
];

export const quickPrompts: QuickPrompt[] = [
  {
    id: "1",
    text: "¿Porciones sugeridas para 7 años (GABA)?",
  },
  {
    id: "3",
    text: "Cómo reducir sodio según guía nacional",
  },
];

export const chatFilters: ChatFilter[] = [
  { id: "1", label: "Dietas", active: false },
  { id: "2", label: "Porciones", active: false },
  { id: "3", label: "Sodio", active: false },
  { id: "4", label: "Azúcares", active: false },
];

export const mockChatHistory = [
  { id: "chat-1", title: "Porciones para niños", date: "2 horas" },
  { id: "chat-2", title: "Dieta baja en sodio", date: "Ayer" },
  { id: "chat-3", title: "Alimentos con hierro", date: "3 días" },
];
