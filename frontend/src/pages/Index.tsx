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
import { mockChatHistory } from '@/data/mockData';
import { api } from '@/services/api';
import { clinicalStorage } from '@/utils/clinicalStorage';
import { toast } from '@/hooks/use-toast';

const Index = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [chatHistory] = useState(mockChatHistory);
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
      // Call API
      setTimeout(() => setTypingStatus('Buscando información en guías oficiales...'), 500);

      const response = await api.query({
        query: content,
        mode,
        clinical_data: isClinicalQuery ? clinicalData || undefined : undefined,
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

  const handleSelectChat = (chatId: string) => {
    setCurrentChatId(chatId);
    // TODO: Cargar mensajes del chat seleccionado
    setMessages([]);
  };

  const handleDeleteChat = (chatId: string) => {
    // TODO: Implementar eliminación de chat
    console.log('Eliminar chat:', chatId);
  };

  return (
    <SidebarProvider>
      <ChatSidebar
        chatHistory={chatHistory}
        currentChatId={currentChatId}
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
