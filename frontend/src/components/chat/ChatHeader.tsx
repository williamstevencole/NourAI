import { NutriaAvatar } from "@/components/NutriaAvatar";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";
import { User } from "lucide-react";

interface ChatHeaderProps {
  onOpenClinicalData?: () => void;
}

export function ChatHeader({ onOpenClinicalData }: ChatHeaderProps) {
  return (
    <header className="h-16 border-b border-border/50 bg-white/80 backdrop-blur-xl sticky top-0 z-40 overflow-hidden">
      <div className="h-full max-w-7xl mx-auto px-6 flex items-center gap-4">
        {/* Sidebar trigger */}
        <SidebarTrigger className="shrink-0" />

        {/* Logo */}
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center ring-1 ring-border/50 shadow-sm overflow-hidden">
            <NutriaAvatar size={56} />
          </div>
          <div>
            <h1 className="text-base font-semibold text-foreground tracking-tight">NutriRAG</h1>
            <p className="text-xs text-muted-foreground/70 leading-tight">
              Asistente nutricional basado en evidencia
            </p>
          </div>
        </div>

        {/* Clinical Data Button */}
        {onOpenClinicalData && (
          <Button
            variant="outline"
            size="sm"
            onClick={onOpenClinicalData}
            className="shrink-0 h-9 rounded-lg border-border/60 hover:bg-muted/50 hover:border-border transition-all"
          >
            <User className="h-3.5 w-3.5 mr-2" />
            <span className="text-sm">Mis Datos</span>
          </Button>
        )}
      </div>
    </header>
  );
}
