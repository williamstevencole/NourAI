import { MessageSquare, Plus, Trash2, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { toast } from "@/hooks/use-toast";
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
} from "@/components/ui/sidebar";

interface ChatHistoryItem {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

interface ChatSidebarProps {
  chatHistory: ChatHistoryItem[];
  currentChatId?: string;
  isTyping?: boolean;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
  onDeleteChat: (chatId: string) => void;
}

export function ChatSidebar({
  chatHistory,
  currentChatId,
  isTyping = false,
  onSelectChat,
  onNewChat,
  onDeleteChat,
}: ChatSidebarProps) {
  return (
    <Sidebar className="bg-background border-r border-border">
      <SidebarHeader className="border-b border-border p-4">
        <Button
          onClick={onNewChat}
          className="w-full justify-start gap-2"
          size="sm"
        >
          <Plus className="h-4 w-4" />
          Nuevo Chat
        </Button>
        <div className="relative mt-2">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input placeholder="Buscar chats..." className="pl-8" />
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Historial de Chats</SidebarGroupLabel>
          <SidebarGroupContent>
            <ScrollArea className="h-[calc(100vh-12rem)]">
              <SidebarMenu className="gap-2">
                {chatHistory.map((chat) => (
                  <SidebarMenuItem key={chat.id}>
                    <div className="group/item relative flex items-center w-full">
                      <SidebarMenuButton
                        isActive={currentChatId === chat.id}
                        onClick={() => {
                          if (isTyping) {
                            toast({
                              title: "Consulta en progreso",
                              description:
                                "Espera a que termine la consulta actual antes de cambiar de chat.",
                              variant: "destructive",
                            });
                            return;
                          }
                          onSelectChat(chat.id);
                        }}
                        className={`flex-1 justify-start gap-2 pr-2 ${
                          isTyping ? "opacity-50 cursor-not-allowed" : ""
                        }`}
                      >
                        <MessageSquare className="h-4 w-4 shrink-0" />
                        <div className="flex flex-col items-start overflow-hidden min-w-0 flex-1">
                          <span className="truncate text-sm font-medium w-full max-w-full">
                            {chat.title}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(chat.updated_at).toLocaleDateString()}
                          </span>
                        </div>
                      </SidebarMenuButton>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="shrink-0 h-7 w-7 opacity-0 group-hover/item:opacity-100 transition-opacity hover:bg-destructive/10"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteChat(chat.id);
                        }}
                        title="Eliminar chat"
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </ScrollArea>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  );
}
