import { quickPrompts } from '@/data/mockData';
import { Badge } from '@/components/ui/badge';
import { NutriaAvatar } from '@/components/NutriaAvatar';
import { Sparkles } from 'lucide-react';

interface EmptyStateProps {
  onPromptClick: (text: string) => void;
}

export function EmptyState({ onPromptClick }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full p-8 overflow-hidden">
      {/* Hero visual con Nutria Avatar */}
      <div className="mb-12 relative">
        <div className="w-24 h-24 rounded-full bg-white flex items-center justify-center ring-1 ring-border/50 shadow-lg overflow-hidden">
          <NutriaAvatar size={100} />
        </div>
        <div className="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-primary/10 flex items-center justify-center backdrop-blur-sm ring-1 ring-primary/20">
          <Sparkles className="w-3.5 h-3.5 text-primary" />
        </div>
      </div>

      {/* Título y descripción */}
      <h2 className="text-3xl font-semibold text-center mb-4 text-foreground tracking-tight">
        Bienvenido a Nourai
      </h2>
      <p className="text-muted-foreground text-center max-w-lg mb-12 text-[15px] leading-relaxed">
        Tu asistente educativo nutricional para el tratamiento y prevención de enfermedades crónicas basado en evidencia científica.
      </p>

      {/* Quick prompts */}
      <div className="space-y-2.5 w-full max-w-2xl">
        <p className="text-sm text-muted-foreground/70 text-center mb-5 font-medium">Prueba con alguna de estas preguntas</p>
        {quickPrompts.map((prompt) => (
          <button
            key={prompt.id}
            onClick={() => onPromptClick(prompt.text)}
            className="w-full p-4 text-left rounded-xl bg-white hover:bg-white/80 border border-border/40 hover:border-primary/30 transition-all group hover:shadow-md hover:-translate-y-0.5"
          >
            <span className="text-[15px] leading-relaxed text-foreground/80 group-hover:text-foreground transition-colors">{prompt.text}</span>
          </button>
        ))}
      </div>

      {/* Info adicional */}
      <div className="mt-16 text-xs text-muted-foreground/60 text-center max-w-lg px-4">
        <p>Las respuestas están basadas en documentación oficial. Siempre consulta con un profesional de la salud para orientación personalizada.</p>
      </div>
    </div>
  );
}
