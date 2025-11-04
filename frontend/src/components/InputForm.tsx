'use client';

import { useState } from 'react';

interface InputFormProps {
  onSubmit: (inputType: 'topic' | 'prompt', inputContent: string) => void;
  isLoading: boolean;
}

export default function InputForm({ onSubmit, isLoading }: InputFormProps) {
  const [inputType, setInputType] = useState<'topic' | 'prompt'>('topic');
  const [inputContent, setInputContent] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputContent.trim()) {
      onSubmit(inputType, inputContent.trim());
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold mb-4 text-gray-800">Generate Post</h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Input Type Toggle */}
        <div className="flex gap-4 mb-4">
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="topic"
              checked={inputType === 'topic'}
              onChange={() => setInputType('topic')}
              className="mr-2"
            />
            <span className="text-gray-700">Topic/Keywords</span>
          </label>
          <label className="flex items-center cursor-pointer">
            <input
              type="radio"
              name="inputType"
              value="prompt"
              checked={inputType === 'prompt'}
              onChange={() => setInputType('prompt')}
              className="mr-2"
            />
            <span className="text-gray-700">Full Prompt</span>
          </label>
        </div>

        {/* Input Field */}
        <div>
          <label htmlFor="inputContent" className="block text-sm font-medium text-gray-700 mb-2">
            {inputType === 'topic' ? 'Enter topic or keywords' : 'Enter full prompt'}
          </label>
          <textarea
            id="inputContent"
            value={inputContent}
            onChange={(e) => setInputContent(e.target.value)}
            placeholder={inputType === 'topic' 
              ? 'e.g., "AI technology trends 2024"' 
              : 'e.g., "Create a post about AI technology trends, focusing on practical applications for businesses"'}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            rows={4}
            required
          />
          <p className="mt-1 text-sm text-gray-500">
            {inputType === 'topic' 
              ? 'Provide a topic or keywords, and the AI will generate a complete post'
              : 'Provide a detailed prompt with context and requirements'}
          </p>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading || !inputContent.trim()}
          className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? 'Generating...' : 'Generate Post'}
        </button>
      </form>
    </div>
  );
}

