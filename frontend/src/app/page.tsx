'use client';

import { useState } from 'react';
import InputForm from '@/components/InputForm';
import OutputDisplay from '@/components/OutputDisplay';
import HistoryList from '@/components/HistoryList';
import { apiService, GenerationResponse } from '@/services/api';

export default function Dashboard() {
  const [currentGeneration, setCurrentGeneration] = useState<GenerationResponse | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [activeTab, setActiveTab] = useState<'generate' | 'history'>('generate');
  const [viewingId, setViewingId] = useState<number | null>(null);

  const handleGenerate = async (inputType: 'topic' | 'prompt', inputContent: string) => {
    setIsGenerating(true);
    setCurrentGeneration(null);
    try {
      const result = await apiService.generatePost({ input_type: inputType, input_content: inputContent });
      setCurrentGeneration(result);
      setActiveTab('generate');
    } catch (error: any) {
      console.error('Generation failed:', error);
      alert(`Failed to generate post: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleViewGeneration = async (id: number) => {
    try {
      const generation = await apiService.getGeneration(id);
      setCurrentGeneration(generation);
      setViewingId(id);
      setActiveTab('generate');
    } catch (error: any) {
      console.error('Failed to load generation:', error);
      alert(`Failed to load generation: ${error.response?.data?.detail || error.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">Runpod Text Models Integration</h1>
          <p className="text-gray-600 mt-1">Generate social media posts using AI models</p>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-6">
        <div className="flex gap-4 border-b border-gray-200">
          <button
            onClick={() => setActiveTab('generate')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'generate'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            Generate Post
          </button>
          <button
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 font-medium ${
              activeTab === 'history'
                ? 'text-primary-600 border-b-2 border-primary-600'
                : 'text-gray-600 hover:text-gray-800'
            }`}
          >
            History
          </button>
        </div>
      </div>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'generate' ? (
          <div className="space-y-6">
            <InputForm onSubmit={handleGenerate} isLoading={isGenerating} />
            <OutputDisplay generation={currentGeneration} isLoading={isGenerating} />
          </div>
        ) : (
          <HistoryList onViewGeneration={handleViewGeneration} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-sm text-gray-600 text-center">
            Powered by Runpod.io - Phi-2 & Mistral 7B Models
          </p>
        </div>
      </footer>
    </div>
  );
}

