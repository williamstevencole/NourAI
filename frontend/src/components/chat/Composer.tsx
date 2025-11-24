import { useState, useRef, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Send } from "lucide-react";
import { quickPrompts } from "@/data/mockData";
import { Badge } from "@/components/ui/badge";

interface ComposerProps {
  onSendMessage: (content: string) => void;
  disabled?: boolean;
}

export function Composer({ onSendMessage, disabled }: ComposerProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput("");
      textareaRef.current?.focus();
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleQuickPrompt = (text: string) => {
    setInput(text);
    textareaRef.current?.focus();
  };

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-white/90 backdrop-blur-xl border-t border-border/50 z-40 transition-[margin] duration-200 ease-linear md:peer-data-[state=expanded]:ml-[var(--sidebar-width)] shadow-[0_-2px_10px_rgba(0,0,0,0.03)]">
      <div className="mx-auto max-w-3xl px-6 py-5">
        {/* Input area */}
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <Textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Escribe tu pregunta sobre nutrición..."
              disabled={disabled}
              className="resize-none min-h-[52px] max-h-[200px] pr-12 bg-white border-border/60 focus:border-primary/50 focus:ring-primary/20 rounded-xl text-[15px] leading-relaxed placeholder:text-muted-foreground/50 transition-all"
              rows={1}
            />
          </div>
          <Button
            onClick={handleSend}
            disabled={!input.trim() || disabled}
            size="icon"
            className="h-[52px] w-[52px] shrink-0 rounded-xl shadow-sm hover:shadow-md transition-all hover:scale-[1.02] disabled:opacity-50 disabled:hover:scale-100"
          >
            <Send className="h-5 w-5" />
          </Button>
        </div>

        <p className="text-xs text-muted-foreground/60 mt-3 text-center">
          NutriRAG puede cometer errores. Verifica información importante.
        </p>
      </div>
    </div>
  );
}
