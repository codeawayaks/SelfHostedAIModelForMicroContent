'use client';

import { useState, useEffect } from 'react';
import { apiService, GenerationListItem } from '@/services/api';
import PreviewCard from './PreviewCard';

interface HistoryListProps {
  onViewGeneration: (id: number) => void;
}

export default function HistoryList({ onViewGeneration }: HistoryListProps) {
  const [generations, setGenerations] = useState<GenerationListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const pageSize = 10;

  const loadHistory = async () => {
    setLoading(true);
    try {
      const response = await apiService.getHistory(page, pageSize);
      setGenerations(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load history:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHistory();
  }, [page]);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this generation?')) {
      return;
    }

    setDeletingId(id);
    try {
      await apiService.deleteGeneration(id);
      await loadHistory();
    } catch (error) {
      console.error('Failed to delete generation:', error);
      alert('Failed to delete generation');
    } finally {
      setDeletingId(null);
    }
  };

  const totalPages = Math.ceil(total / pageSize);

  if (loading && generations.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <p className="text-gray-500 text-center">Loading history...</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-gray-800">Generation History</h2>
        <span className="text-sm text-gray-600">
          {total} total {total === 1 ? 'generation' : 'generations'}
        </span>
      </div>

      {generations.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No generations yet. Create your first post!</p>
      ) : (
        <>
          <div className="space-y-4 mb-6">
            {generations.map((generation) => (
              <PreviewCard
                key={generation.id}
                generation={generation}
                onView={onViewGeneration}
                onDelete={handleDelete}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <span className="text-sm text-gray-600">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

