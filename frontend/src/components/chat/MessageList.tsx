import { Message } from '@/types/chat';
import { MessageBubble } from './MessageBubble';
import { ScrollArea } from '@/components/ui/scroll-area';
import { NutriaAvatar } from '@/components/NutriaAvatar';
import { useEffect, useRef, memo } from 'react';

interface MessageListProps {
  messages: Message[];
  isTyping?: boolean;
  typingStatus?: string;
}

// Memoize TypingIndicator since it doesn't depend on message list
const TypingIndicator = memo(function TypingIndicator({ typingStatus }: { typingStatus: string }) {
  return (
    <div className="flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300 mb-6">
      <div className="shrink-0">
        <div className="w-10 h-10 rounded-full flex items-center justify-center bg-white ring-1 ring-border/50 shadow-sm overflow-hidden">
          <NutriaAvatar size={56} />
        </div>
      </div>
      <div className="flex-1 max-w-[75%] space-y-2">
        <div className="rounded-2xl rounded-bl-md px-5 py-3.5 bg-white border border-border/60 shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
            <div className="w-2 h-2 bg-primary/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
          </div>
          <p className="text-xs text-muted-foreground/70 font-medium">{typingStatus}</p>
        </div>
      </div>
    </div>
  );
});

export function MessageList({ messages, isTyping, typingStatus = 'Analizando tu pregunta...' }: MessageListProps) {
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  // Auto-scroll al último mensaje
  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping, typingStatus]);

  return (
    <ScrollArea className="h-full">
      <div className="pb-44 px-6 max-w-5xl mx-auto py-8">
        {messages.map((message, index) => (
          <div
            key={message.id}
            className="animate-in fade-in slide-in-from-bottom-3 duration-400"
            style={{ animationDelay: `${index * 50}ms`, animationFillMode: 'backwards' }}
          >
            <MessageBubble message={message} />
          </div>
        ))}

        {/* Typing indicator with status */}
        {isTyping && <TypingIndicator typingStatus={typingStatus} />}

        {/* Invisible anchor for auto-scroll */}
        <div ref={endOfMessagesRef} />
      </div>
    </ScrollArea>
  );
}
