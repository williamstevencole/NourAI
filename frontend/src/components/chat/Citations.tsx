import { useState } from 'react';
import { Citation } from '@/types/chat';
import { Source } from '@/services/api';
import { Badge } from '@/components/ui/badge';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CitationsProps {
  citations?: Citation[];
  sources?: Source[];
}

export function Citations({ citations }: CitationsProps) {
  const [openCitations, setOpenCitations] = useState<Set<string>>(new Set());

  const toggleCitation = (id: string) => {
    setOpenCitations((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  if (!citations || citations.length === 0) {
    return null;
  }

  return (
    <div className="mt-3 space-y-2">
      <div className="text-xs font-medium text-muted-foreground mb-2">Fuentes:</div>
      <div className="flex flex-wrap gap-2">
        {citations.map((citation) => {
          const isOpen = openCitations.has(citation.id);

          return (
            <Collapsible
              key={citation.id}
              open={isOpen}
              onOpenChange={() => toggleCitation(citation.id)}
              className="w-full"
            >
              <CollapsibleTrigger asChild>
                <Badge
                  variant="outline"
                  className={cn(
                    "cursor-pointer hover:bg-primary/10 transition-all text-xs gap-1",
                    isOpen && "bg-primary/10"
                  )}
                >
                  {citation.label} {citation.organization}
                  {isOpen ? (
                    <ChevronUp className="h-3 w-3" />
                  ) : (
                    <ChevronDown className="h-3 w-3" />
                  )}
                </Badge>
              </CollapsibleTrigger>

              <CollapsibleContent className="mt-2">
                <div className="bg-muted/50 rounded-lg p-3 space-y-2 text-xs border border-border">
                  <div>
                    <span className="font-semibold">Título:</span>{' '}
                    <span className="text-muted-foreground">{citation.title}</span>
                  </div>

                  <div>
                    <span className="font-semibold">Organización:</span>{' '}
                    <span className="text-muted-foreground">{citation.organization}</span>
                  </div>

                  {citation.year && (
                    <div>
                      <span className="font-semibold">Año:</span>{' '}
                      <span className="text-muted-foreground">{citation.year}</span>
                    </div>
                  )}

                  {citation.excerpt && (
                    <div>
                      <span className="font-semibold">Similitud:</span>{' '}
                      <span className="text-muted-foreground">{citation.excerpt}</span>
                    </div>
                  )}

                  {citation.url && (
                    <div>
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-primary hover:underline"
                      >
                        Ver documento
                        <ExternalLink className="h-3 w-3" />
                      </a>
                    </div>
                  )}
                </div>
              </CollapsibleContent>
            </Collapsible>
          );
        })}
      </div>
    </div>
  );
}

