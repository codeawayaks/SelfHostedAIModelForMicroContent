'use client';

import { GenerationListItem } from '@/services/api';

interface PreviewCardProps {
  generation: GenerationListItem;
  onView: (id: number) => void;
  onDelete: (id: number) => void;
}

export default function PreviewCard({ generation, onView, onDelete }: PreviewCardProps) {
  const previewText = generation.final_output.length > 150 
    ? generation.final_output.substring(0, 150) + '...'
    : generation.final_output;

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs px-2 py-1 bg-primary-100 text-primary-700 rounded">
              {generation.input_type}
            </span>
            <span className="text-xs text-gray-500">
              ${generation.cost.toFixed(5)}
            </span>
          </div>
          <p className="text-sm font-medium text-gray-800 mb-1">
            {generation.input_content.length > 60
              ? generation.input_content.substring(0, 60) + '...'
              : generation.input_content}
          </p>
        </div>
      </div>
      
      <p className="text-sm text-gray-600 mb-3 line-clamp-3">
        {previewText}
      </p>
      
      <div className="flex justify-between items-center">
        <span className="text-xs text-gray-500">
          {new Date(generation.timestamp).toLocaleString()}
        </span>
        <div className="flex gap-2">
          <button
            onClick={() => onView(generation.id)}
            className="text-sm text-primary-600 hover:text-primary-700 font-medium"
          >
            View
          </button>
          <button
            onClick={() => onDelete(generation.id)}
            className="text-sm text-red-600 hover:text-red-700 font-medium"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}

