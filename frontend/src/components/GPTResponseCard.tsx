import React from 'react';
import { Bot, ThumbsUp, ThumbsDown } from 'lucide-react';

interface GPTResponseCardProps {
  question?: string;
  response: string;
  loading?: boolean;
  className?: string;
  sources?: { text: string; url: string }[];
}

export default function GPTResponseCard({ 
  question, 
  response, 
  loading = false,
  className = '',
  sources = []
}: GPTResponseCardProps) {
  return (
    <div className={`rounded-lg border bg-white dark:bg-gray-800 text-card-foreground shadow-sm ${className}`}>
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-4 rounded-t-lg">
        <div className="flex items-center gap-3">
          <div className="bg-white/20 p-2 rounded-full">
            <Bot size={24} className="text-white" />
          </div>
          <h3 className="text-lg font-bold text-white">AI Insights</h3>
        </div>
      </div>
      
      <div className="p-6">
        {question && (
          <div className="mt-1 mb-4 rounded-md bg-gray-100 dark:bg-gray-700 p-3">
            <p className="text-sm font-medium">Question:</p>
            <p className="mt-1 text-sm">{question}</p>
          </div>
        )}
        
        <div className="mt-2">
          {loading ? (
            <div className="flex items-center justify-center py-8">
              <div className="h-6 w-6 animate-spin rounded-full border-2 border-blue-600 border-t-transparent"></div>
            </div>
          ) : (
            <>
              <div className="prose prose-sm max-w-none dark:prose-invert">
                {response.split('\n').map((paragraph, index) => (
                  paragraph.trim() ? <p key={index} className="mb-3">{paragraph}</p> : <br key={index} />
                ))}
              </div>
              
              {sources.length > 0 && (
                <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Sources</h4>
                  <ul className="space-y-2">
                    {sources.map((source, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <a 
                          href={source.url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 dark:text-blue-400 hover:underline"
                        >
                          {source.text}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="mt-6 flex items-center justify-end gap-2">
                <button className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                  <ThumbsUp className="h-4 w-4" />
                  <span>Helpful</span>
                </button>
                <button className="inline-flex items-center gap-1 rounded-md bg-gray-100 px-2.5 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
                  <ThumbsDown className="h-4 w-4" />
                  <span>Not helpful</span>
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
