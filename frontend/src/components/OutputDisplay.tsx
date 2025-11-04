'use client';

import { useState } from 'react';
import { GenerationResponse } from '@/services/api';

interface OutputDisplayProps {
  generation: GenerationResponse | null;
  isLoading: boolean;
}

export default function OutputDisplay({ generation, isLoading }: OutputDisplayProps) {
  const [copied, setCopied] = useState(false);

  const copyToClipboard = () => {
    if (generation?.final_output) {
      // Strip metadata and copy only the clean output
      navigator.clipboard.writeText(generation.final_output.trim());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        </div>
      </div>
    );
  }

  if (!generation) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center">Generated post will appear here</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Generated Post</h2>
        <button
          onClick={copyToClipboard}
          className="bg-primary-600 text-white px-4 py-2 rounded-md hover:bg-primary-700 transition-colors"
        >
          {copied ? '✓ Copied!' : 'Copy to Clipboard'}
        </button>
      </div>

      {/* Cost Breakdown */}
      <div className="mb-6 p-4 bg-gray-50 rounded-md">
        <h3 className="text-sm font-semibold text-gray-700 mb-2">Cost Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
          <div>
            <span className="text-gray-600">Hook:</span>
            <span className="ml-1 font-medium">${generation.hook_cost.toFixed(5)}</span>
          </div>
          <div>
            <span className="text-gray-600">Caption:</span>
            <span className="ml-1 font-medium">${generation.caption_cost.toFixed(5)}</span>
          </div>
          <div>
            <span className="text-gray-600">CTA:</span>
            <span className="ml-1 font-medium">${generation.cta_cost.toFixed(5)}</span>
          </div>
          <div>
            <span className="text-gray-600">Merge:</span>
            <span className="ml-1 font-medium">${generation.merge_cost.toFixed(5)}</span>
          </div>
          <div className="col-span-2 md:col-span-1">
            <span className="text-gray-600">Total:</span>
            <span className="ml-1 font-bold text-primary-600">${generation.cost.toFixed(5)}</span>
          </div>
        </div>
      </div>

      {/* Component Previews */}
      <div className="space-y-4 mb-6">
        {generation.hook && (
          <div className="p-3 bg-blue-50 border-l-4 border-blue-500 rounded">
            <h4 className="text-sm font-semibold text-blue-800 mb-1">Hook</h4>
            <p className="text-gray-700">{generation.hook}</p>
          </div>
        )}
        {generation.caption && (
          <div className="p-3 bg-green-50 border-l-4 border-green-500 rounded">
            <h4 className="text-sm font-semibold text-green-800 mb-1">Caption</h4>
            <p className="text-gray-700">{generation.caption}</p>
          </div>
        )}
        {generation.cta && (
          <div className="p-3 bg-purple-50 border-l-4 border-purple-500 rounded">
            <h4 className="text-sm font-semibold text-purple-800 mb-1">Call-to-Action</h4>
            <p className="text-gray-700">{generation.cta}</p>
          </div>
        )}
      </div>

      {/* Final Output */}
      <div className="border-t pt-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-3">Final Output</h3>
        <div className="bg-gray-50 p-4 rounded-md border">
          <pre className="whitespace-pre-wrap text-gray-800 font-sans">
            {generation.final_output.trim()}
          </pre>
        </div>
      </div>
    </div>
  );
}

