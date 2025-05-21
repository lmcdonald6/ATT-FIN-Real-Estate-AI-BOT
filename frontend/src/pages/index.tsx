import React, { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { Home as HomeIcon, Search, TrendingUp, Map, Users, MessageSquare } from 'lucide-react';
import ZipSearch from '../components/ZipSearch';
import GPTChatPanel from '../components/GPTChatPanel';

export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = (zip: string) => {
    setIsLoading(true);
    // Navigate to dashboard with the ZIP code
    router.push(`/dashboard?zip=${zip}`);
  };

  return (
    <>
      <Head>
        <title>Neighborhood Sentiment Portal</title>
        <meta name="description" content="Analyze neighborhood sentiment and trends" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        <div className="container mx-auto px-4 py-12">
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Neighborhood Sentiment Portal
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              AI-Powered Real Estate Intelligence for Informed Decisions
            </p>
          </div>

          <div className="max-w-xl mx-auto mb-16">
            <ZipSearch onSearch={handleSearch} isLoading={isLoading} />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-full mb-4">
                <Search className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Sentiment Analysis</h3>
              <p className="text-gray-600">
                Discover how neighborhoods are perceived through our advanced AI sentiment analysis of social media, news, and local data.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
                <TrendingUp className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Trend Tracking</h3>
              <p className="text-gray-600">
                Track neighborhood trends over time to identify emerging areas and investment opportunities before they become mainstream.
              </p>
            </div>

            <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-full mb-4">
                <Users className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Persona Matching</h3>
              <p className="text-gray-600">
                Find the perfect neighborhood match based on your lifestyle, preferences, and needs with our persona matching technology.
              </p>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8 mb-16">
            <h2 className="text-2xl font-bold mb-6 text-center">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                  <span className="text-2xl font-bold text-gray-700">1</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">Enter ZIP Code</h3>
                <p className="text-gray-600">Start by entering any U.S. ZIP code to analyze the neighborhood sentiment.</p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                  <span className="text-2xl font-bold text-gray-700">2</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">AI Analysis</h3>
                <p className="text-gray-600">Our AI engine analyzes thousands of data points to generate comprehensive insights.</p>
              </div>
              
              <div className="text-center">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-100 rounded-full mb-4">
                  <span className="text-2xl font-bold text-gray-700">3</span>
                </div>
                <h3 className="text-lg font-semibold mb-2">Get Results</h3>
                <p className="text-gray-600">Review detailed sentiment analysis, trends, and neighborhood compatibility scores.</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-8 mb-16">
            <div className="flex items-center mb-6">
              <div className="flex items-center justify-center w-12 h-12 bg-indigo-100 rounded-full mr-4">
                <MessageSquare className="w-6 h-6 text-indigo-600" />
              </div>
              <h2 className="text-2xl font-bold">Ask Our AI Assistant</h2>
            </div>
            <GPTChatPanel />
          </div>

          <div className="text-center">
            <h2 className="text-2xl font-bold mb-4">Ready to discover your ideal neighborhood?</h2>
            <p className="text-gray-600 mb-6">Enter a ZIP code above to get started or explore our advanced features.</p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
                Learn More
              </button>
              <button className="px-6 py-3 border border-blue-600 text-blue-600 rounded-md hover:bg-blue-50 transition-colors">
                View Demo
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
