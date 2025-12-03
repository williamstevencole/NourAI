import { useState, useEffect } from 'react';
import { ChatHeader } from '@/components/chat/ChatHeader';
import { MessageList } from '@/components/chat/MessageList';
import { Composer } from '@/components/chat/Composer';
import { EmptyState } from '@/components/chat/EmptyState';
import { FruitsBackground } from '@/components/background/FruitsBackground';
import { ChatSidebar } from '@/components/ChatSidebar';
import { SidebarProvider, SidebarInset } from '@/components/ui/sidebar';
import { ClinicalDataDialog } from '@/components/ClinicalDataDialog';
import { Message, ClinicalData } from '@/types/chat';
import { Chat } from '@/services/api';
import { api } from '@/services/api';
import { clinicalStorage } from '@/utils/clinicalStorage';
import { toast } from '@/hooks/use-toast';

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatHistory, setChatHistory] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | undefined>();
  const [isTyping, setIsTyping] = useState(false);
  const [typingStatus, setTypingStatus] = useState('Analizando tu pregunta...');
  const [clinicalData, setClinicalData] = useState<ClinicalData | null>(null);
  const [showClinicalDialog, setShowClinicalDialog] = useState(false);

  // Load clinical data from local storage on mount
  useEffect(() => {
    const savedData = clinicalStorage.load();
    if (savedData) {
      setClinicalData(savedData);
    } else {
      // Show dialog on first visit
      setShowClinicalDialog(true);
    }
  }, []);

  // Load chat history on mount
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const response = await api.listChats();
        setChatHistory(response.chats);
      } catch (error) {
        console.error('Failed to load chat history:', error);
        // Keep empty chat history on error
      }
    };

    loadChatHistory();
  }, []);

  const handleSaveClinicalData = (data: ClinicalData) => {
    clinicalStorage.save(data);
    setClinicalData(data);
    toast({
      title: 'Información guardada',
      description: 'Tus datos clínicos han sido guardados localmente.',
    });
  };

  const handleDeleteClinicalData = () => {
    clinicalStorage.clear();
    setClinicalData(null);
    toast({
      title: 'Datos borrados',
      description: 'Tus datos clínicos han sido eliminados.',
    });
  };

  const detectClinicalQuery = (query: string): boolean => {
    const clinicalKeywords = [
      'diabetes',
      'hipertensión',
      'colesterol',
      'peso',
      'dieta',
      'nutrición',
      'calorías',
      'imc',
      'obesidad',
      'adelgazar',
      'engordar',
      'enfermedad',
      'condición',
      'alergia',
      'medicamento',
    ];
    const lowerQuery = query.toLowerCase();
    return clinicalKeywords.some((keyword) => lowerQuery.includes(keyword));
  };

  const handleSendMessage = async (content: string) => {
    let chatId = currentChatId;

    // Create new chat if none exists
    if (!chatId) {
      try {
        const chatResponse = await api.createChat(content.length > 50 ? content.substring(0, 50) + '...' : content);
        chatId = chatResponse.chat_id;
        setCurrentChatId(chatId);

        // Refresh chat history
        const historyResponse = await api.listChats();
        setChatHistory(historyResponse.chats);
      } catch (error) {
        console.error('Failed to create chat:', error);
        toast({
          title: 'Error',
          description: 'No se pudo crear el chat.',
          variant: 'destructive',
        });
        return;
      }
    }

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMessage]);

    // Check if this is a clinical query
    const isClinicalQuery = detectClinicalQuery(content);
    const mode = isClinicalQuery ? 'clinical' : 'general';

    // Show typing indicator
    setIsTyping(true);
    setTypingStatus('Analizando tu pregunta...');

    try {
      // Call API with chat_id
      setTimeout(() => setTypingStatus('Buscando información en guías oficiales...'), 500);

      const response = await api.query({
        query: content,
        mode,
        clinical_data: isClinicalQuery ? clinicalData || undefined : undefined,
        chat_id: chatId,
      });

      setTypingStatus('Generando respuesta...');

      // Convert sources to citations
      const citations = response.sources.map((source, idx) => ({
        id: `cite-${idx}`,
        label: `[${idx + 1}]`,
        organization: source.organization,
        year: source.year?.toString() || '',
        title: source.title,
        url: source.link,
        excerpt: `Similitud: ${source.similarity}`,
      }));

      // Add assistant message
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.answer,
        citations,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Refresh chat history to update timestamps
      const historyResponse = await api.listChats();
      setChatHistory(historyResponse.chats);
    } catch (error) {
      console.error('Error querying API:', error);

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Lo siento, ocurrió un error al procesar tu pregunta. Por favor, verifica que el servidor esté funcionando y vuelve a intentarlo.\n\nError: ${error instanceof Error ? error.message : 'Error desconocido'}`,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);

      toast({
        title: 'Error',
        description: 'No se pudo conectar con el servidor. Verifica que esté corriendo.',
        variant: 'destructive',
      });
    } finally {
      setIsTyping(false);
    }
  };

  const handlePromptClick = (text: string) => {
    handleSendMessage(text);
  };

  const handleNewChat = () => {
    setMessages([]);
    setCurrentChatId(undefined);
  };

  const handleSelectChat = async (chatId: string) => {
    setCurrentChatId(chatId);
    setIsTyping(false); // Clear any typing state

    try {
      const response = await api.getChat(chatId);
      const loadedMessages: Message[] = response.messages.map(msg => {
        // Convert sources to citations for loaded messages (same as fresh responses)
        let citations = msg.citations;
        if (msg.sources && msg.sources.length > 0) {
          citations = msg.sources.map((source, idx) => ({
            id: `cite-${idx}`,
            label: `[${idx + 1}]`,
            organization: source.organization,
            year: source.year?.toString() || '',
            title: source.title,
            url: source.link,
            excerpt: `Similitud: ${source.similarity}`,
          }));
        }

        return {
          id: msg.id,
          role: msg.role,
          content: msg.content,
          citations,
          sources: msg.sources,
          timestamp: new Date(msg.timestamp),
        };
      });
      console.log(loadedMessages)
      setMessages(loadedMessages);
    } catch (error) {
      console.error('Failed to load chat:', error);
      setMessages([]);
      toast({
        title: 'Error',
        description: 'No se pudieron cargar los mensajes del chat.',
        variant: 'destructive',
      });
    }
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      await api.deleteChat(chatId);

      // Refresh chat history
      const response = await api.listChats();
      setChatHistory(response.chats);

      // If current chat was deleted, reset state
      if (currentChatId === chatId) {
        setCurrentChatId(undefined);
        setMessages([]);
      }

      toast({
        title: 'Chat eliminado',
        description: 'El chat ha sido eliminado exitosamente.',
      });
    } catch (error) {
      console.error('Failed to delete chat:', error);
      toast({
        title: 'Error',
        description: 'No se pudo eliminar el chat.',
        variant: 'destructive',
      });
    }
  };

  return (
    <SidebarProvider>
      <ChatSidebar
        chatHistory={chatHistory}
        currentChatId={currentChatId}
        isTyping={isTyping}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
        onDeleteChat={handleDeleteChat}
      />
      <SidebarInset className="flex flex-col pb-36">
        <FruitsBackground />
        <ChatHeader onOpenClinicalData={() => setShowClinicalDialog(true)} />

        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col overflow-hidden relative z-10">
          {messages.length === 0 ? (
            <EmptyState onPromptClick={handlePromptClick} />
          ) : (
            <MessageList messages={messages} isTyping={isTyping} typingStatus={typingStatus} />
          )}
        </main>
      </SidebarInset>

      {/* Composer - Fixed vertically, follows horizontal layout */}
      <Composer onSendMessage={handleSendMessage} disabled={isTyping} />

      {/* Clinical Data Dialog */}
      <ClinicalDataDialog
        open={showClinicalDialog}
        onOpenChange={setShowClinicalDialog}
        onSave={handleSaveClinicalData}
        onDelete={handleDeleteClinicalData}
        initialData={clinicalData || undefined}
      />
    </SidebarProvider>
  );
};

export default Index;
