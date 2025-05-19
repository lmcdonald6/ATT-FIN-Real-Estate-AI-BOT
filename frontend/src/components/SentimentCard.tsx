import React from 'react';
import { Gauge, TrendingUp, MessageSquare } from 'lucide-react';

interface SentimentCardProps {
  zipCode?: string;
  city?: string;
  state?: string;
  score: number;
  keywords: string[];
  topics: string[];
  summary?: string;
  className?: string;
}

export default function SentimentCard({ 
  zipCode,
  city,
  state,
  score, 
  keywords = [], 
  topics = [], 
  summary,
  className = '' 
}: SentimentCardProps) {
  // Helper function to get sentiment description and color
  const getSentimentInfo = (score: number) => {
    if (score >= 80) return { description: 'Excellent', color: 'text-green-600' };
    if (score >= 70) return { description: 'Very Good', color: 'text-emerald-600' };
    if (score >= 60) return { description: 'Good', color: 'text-blue-600' };
    if (score >= 50) return { description: 'Average', color: 'text-yellow-600' };
    if (score >= 40) return { description: 'Below Average', color: 'text-orange-600' };
    if (score >= 30) return { description: 'Poor', color: 'text-red-600' };
    return { description: 'Very Poor', color: 'text-red-700' };
  };

  const { description, color } = getSentimentInfo(score);

  return (
    <div className={`rounded-lg border bg-white dark:bg-gray-800 text-card-foreground shadow-sm ${className}`}>
      <div className="p-6">
        {(city || state || zipCode) && (
          <div className="mb-4">
            <h2 className="text-xl font-bold">
              {city && state ? `${city}, ${state}` : ''} {zipCode}
            </h2>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Neighborhood Sentiment</h3>
          <Gauge className="h-5 w-5 text-muted-foreground" />
        </div>
        
        <div className="mt-4 flex items-center justify-center">
          <div className="relative h-32 w-32">
            <svg className="h-full w-full" viewBox="0 0 100 100">
              <circle
                className="text-gray-200 dark:text-gray-700"
                strokeWidth="10"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
              />
              <circle
                className={color}
                strokeWidth="10"
                strokeDasharray={`${score * 2.51} 251`}
                strokeLinecap="round"
                stroke="currentColor"
                fill="transparent"
                r="40"
                cx="50"
                cy="50"
                transform="rotate(-90 50 50)"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-3xl font-bold ${color}`}>{score}</span>
              <span className="text-sm text-muted-foreground">{description}</span>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium">Trending Keywords</h4>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {keywords.length > 0 ? (
              keywords.map((keyword, index) => (
                <span
                  key={index}
                  className="inline-flex items-center rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-medium text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                >
                  {keyword}
                </span>
              ))
            ) : (
              <span className="text-sm text-muted-foreground">No keywords available</span>
            )}
          </div>
        </div>

        <div className="mt-4">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
            <h4 className="font-medium">Trending Topics</h4>
          </div>
          <div className="mt-2 flex flex-wrap gap-2">
            {topics.length > 0 ? (
              topics.map((topic, index) => (
                <span
                  key={index}
                  className="inline-flex items-center rounded-full bg-purple-100 px-2.5 py-0.5 text-xs font-medium text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                >
                  {topic}
                </span>
              ))
            ) : (
              <span className="text-sm text-muted-foreground">No topics available</span>
            )}
          </div>
        </div>

        {summary && (
          <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-300">{summary}</p>
          </div>
        )}
      </div>
    </div>
  );
}
