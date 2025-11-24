import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Copy, Check } from 'lucide-react';
import { useState } from 'react';
import { toast } from 'sonner';
import { Button } from '@/components/ui/button';
import type { Components } from 'react-markdown';

interface MarkdownRendererProps {
  content: string;
}

export const MarkdownRenderer: React.FC<MarkdownRendererProps> = ({ content }) => {
  const [copiedBlocks, setCopiedBlocks] = useState<Set<number>>(new Set());

  const handleCopyCode = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedBlocks(prev => new Set(prev).add(index));
      toast.success('Código copiado al portapapeles');
      setTimeout(() => {
        setCopiedBlocks(prev => {
          const newSet = new Set(prev);
          newSet.delete(index);
          return newSet;
        });
      }, 2000);
    } catch (err) {
      toast.error('Error al copiar el código');
    }
  };

  return (
    <div className="prose prose-sm max-w-none prose-headings:text-foreground prose-strong:text-foreground prose-a:text-primary prose-a:no-underline hover:prose-a:underline prose-blockquote:border-l-primary prose-blockquote:text-muted-foreground prose-code:text-foreground prose-pre:bg-transparent prose-pre:p-0">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Headings
          h1: ({ children }) => (
            <h1 className="text-2xl font-bold mt-8 mb-4 text-foreground first:mt-0">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-bold mt-7 mb-3 text-foreground">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold mt-6 mb-3 text-foreground">{children}</h3>
          ),
          h4: ({ children }) => (
            <h4 className="text-base font-semibold mt-5 mb-2 text-foreground">{children}</h4>
          ),
          h5: ({ children }) => (
            <h5 className="text-sm font-semibold mt-4 mb-2 text-foreground">{children}</h5>
          ),
          h6: ({ children }) => (
            <h6 className="text-sm font-semibold mt-4 mb-2 text-foreground">{children}</h6>
          ),

          // Paragraphs
          p: ({ children }) => (
            <p className="mb-4 last:mb-0 text-foreground/90 leading-relaxed">{children}</p>
          ),

          // Lists
          ul: ({ children }) => (
            <ul className="list-disc list-outside ml-6 mb-4 space-y-2">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-outside ml-6 mb-4 space-y-2">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="text-foreground/90 leading-relaxed">{children}</li>
          ),

          // Blockquotes
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-primary/30 pl-4 py-2 my-4 bg-muted/20 rounded-r-md italic text-muted-foreground">
              {children}
            </blockquote>
          ),

          // Tables
          table: ({ children }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full border-collapse border border-border rounded-lg overflow-hidden">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-muted/50">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-border">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-muted/20">{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-sm font-semibold text-foreground border-r border-border last:border-r-0">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-foreground/90 border-r border-border last:border-r-0">
              {children}
            </td>
          ),

          // Code blocks
          code: (props) => {
            const { children, className, ...rest } = props;
            const match = /language-(\w+)/.exec(className || '');
            const codeContent = String(children).replace(/\n$/, '');
            const isInline = !match;

            if (!isInline) {
              const language = match[1];
              const blockIndex = Math.random(); // Simple index for copy state

              return (
                <div className="relative group my-4">
                  <div className="flex items-center justify-between px-4 py-2 bg-muted/50 border border-border rounded-t-lg">
                    <span className="text-xs font-mono text-muted-foreground">{language}</span>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                      onClick={() => handleCopyCode(codeContent, blockIndex)}
                    >
                      {copiedBlocks.has(blockIndex) ? (
                        <Check className="h-3 w-3 text-green-600" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                  <SyntaxHighlighter
                    style={oneLight as any}
                    language={language}
                    PreTag="div"
                    className="!mt-0 !rounded-t-none !rounded-b-lg !bg-muted/30"
                    customStyle={{
                      margin: 0,
                      padding: '1rem',
                      fontSize: '0.875rem',
                      lineHeight: '1.5',
                    }}
                  >
                    {codeContent}
                  </SyntaxHighlighter>
                </div>
              );
            }

            // Inline code
            return (
              <code
                className="bg-muted/60 px-1.5 py-0.5 rounded text-sm font-mono text-foreground"
                {...rest}
              >
                {children}
              </code>
            );
          },

          // Links
          a: ({ children, href }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:text-primary/80 underline underline-offset-2 transition-colors"
            >
              {children}
            </a>
          ),

          // Emphasis
          strong: ({ children }) => (
            <strong className="font-semibold text-foreground">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-foreground/90">{children}</em>
          ),

          // Horizontal rule
          hr: () => (
            <hr className="my-6 border-border" />
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};