import { Message } from '@/types/chat';
import { Button } from '@/components/ui/button';
import { Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import { useState, memo } from 'react';
import { toast } from 'sonner';
import { NutriaAvatar } from '@/components/NutriaAvatar';
import { Citations } from './Citations';
import { MarkdownRenderer } from './MarkdownRenderer';

interface MessageBubbleProps {
  message: Message;
}

export const MessageBubble = memo(function MessageBubble({ message }: MessageBubbleProps) {
  const [reaction, setReaction] = useState<'up' | 'down' | null>(null);
  const isUser = message.role === 'user';

  const handleCopy = () => {
    navigator.clipboard.writeText(message.content);
    toast.success('Copiado al portapapeles');
  };

  const handleReaction = (type: 'up' | 'down') => {
    setReaction(reaction === type ? null : type);
    toast.success(reaction === type ? 'Reacción eliminada' : 'Gracias por tu feedback');
  };

  return (
    <div className={`flex gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} group mb-6`}>
      {/* Avatar */}
      <div className="shrink-0">
        <div
          className={`w-10 h-10 rounded-full flex items-center justify-center overflow-hidden transition-all ${isUser
              ? 'bg-gradient-to-br from-primary/10 to-primary/5 ring-1 ring-primary/20'
              : 'bg-white ring-1 ring-border/50 shadow-sm'
            }`}
        >
          {isUser ? (
            <span className="text-base">👤</span>
          ) : (
            <NutriaAvatar size={56} />
          )}
        </div>
      </div>

      {/* Content */}
      <div className={`flex-1 max-w-[85%] ${isUser ? 'flex justify-end' : ''}`}>
        <div className="space-y-2.5">
          {/* Message bubble */}
          <div
            className={`rounded-2xl px-5 py-3.5 transition-all ${isUser
                ? 'bg-primary text-primary-foreground rounded-br-md shadow-sm hover:shadow-md'
                : 'bg-white text-card-foreground rounded-bl-md border border-border/60 shadow-sm hover:shadow-md hover:border-border'
              }`}
          >
            {isUser ? (
              <p className="text-[15px] leading-relaxed">{message.content}</p>
            ) : (
              <div className="text-[15px] leading-relaxed">
                <MarkdownRenderer content={message.content} />
              </div>
            )}
          </div>

          {/* Citations */}
          {!isUser && (message.citations || message.sources) && (
            <Citations citations={message.citations} sources={message.sources} />
          )}

          {/* Actions bar */}
          {!isUser && (
            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-all duration-200">
              <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-muted/80 rounded-lg transition-all" onClick={handleCopy}>
                <Copy className="h-3.5 w-3.5 text-muted-foreground" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 hover:bg-muted/80 rounded-lg transition-all"
                onClick={() => handleReaction('up')}
              >
                <ThumbsUp className={`h-3.5 w-3.5 transition-colors ${reaction === 'up' ? 'fill-primary text-primary' : 'text-muted-foreground'}`} />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 hover:bg-muted/80 rounded-lg transition-all"
                onClick={() => handleReaction('down')}
              >
                <ThumbsDown className={`h-3.5 w-3.5 transition-colors ${reaction === 'down' ? 'fill-destructive text-destructive' : 'text-muted-foreground'}`} />
              </Button>
            </div>
          )}

          {/* Timestamp */}
          <p className={`text-xs text-muted-foreground/70 font-medium ${isUser ? 'text-right' : 'text-left'} mt-1`}>
            {message.timestamp.toLocaleTimeString('es-HN', { hour: '2-digit', minute: '2-digit' })}
          </p>
        </div>
      </div>
    </div>
  );
});
