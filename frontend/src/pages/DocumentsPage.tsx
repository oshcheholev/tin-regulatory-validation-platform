import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService } from '@/services';
import { Card, Button, Badge, Spinner, EmptyState } from '@/components/common';
import { Upload, FileText, Trash2, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Document } from '@/types';

const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
};

const statusVariant: Record<Document['status'], 'default' | 'warning' | 'success' | 'error' | 'info'> = {
  pending: 'warning',
  processing: 'info',
  completed: 'success',
  failed: 'error',
};

const DocumentsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentService.list(),
    refetchInterval: 5000, // Poll every 5s for status updates
  });

  const uploadMutation = useMutation({
    mutationFn: (formData: FormData) => documentService.upload(formData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document uploaded and queued for processing');
      setTitle('');
      setDescription('');
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    },
    onError: () => toast.error('Upload failed. Please check the file and try again.'),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => documentService.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      toast.success('Document deleted');
    },
    onError: () => toast.error('Failed to delete document'),
  });

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile || !title.trim()) {
      toast.error('Please provide a title and select a PDF file');
      return;
    }
    const formData = new FormData();
    formData.append('title', title.trim());
    formData.append('description', description.trim());
    formData.append('file', selectedFile);
    uploadMutation.mutate(formData);
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">OECD Documents</h1>
          <p className="text-gray-500 mt-1">Upload PDF documents to extract TIN validation rules</p>
        </div>
        <Button variant="outline" onClick={() => refetch()} size="sm">
          <RefreshCw size={14} className="mr-1" />
          Refresh
        </Button>
      </div>

      {/* Upload card */}
      <Card title="Upload Document">
        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Document Title *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. OECD TIN Guide 2024"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional description..."
              rows={2}
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">PDF File *</label>
            <div
              className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors cursor-pointer"
              onClick={() => fileInputRef.current?.click()}
            >
              <Upload size={24} className="mx-auto text-gray-400 mb-2" />
              {selectedFile ? (
                <p className="text-sm text-gray-700 font-medium">{selectedFile.name}</p>
              ) : (
                <>
                  <p className="text-sm text-gray-500">Click to select a PDF</p>
                  <p className="text-xs text-gray-400 mt-1">Max 20MB</p>
                </>
              )}
              <input
                ref={fileInputRef}
                type="file"
                accept="application/pdf"
                className="hidden"
                onChange={(e) => setSelectedFile(e.target.files?.[0] ?? null)}
              />
            </div>
          </div>
          <Button type="submit" isLoading={uploadMutation.isPending}>
            <Upload size={16} className="mr-2" />
            Upload & Process
          </Button>
        </form>
      </Card>

      {/* Document list */}
      <Card title={`Documents (${data?.count ?? 0})`}>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : data?.results.length === 0 ? (
          <EmptyState message="No documents uploaded yet" icon={<FileText size={32} />} />
        ) : (
          <div className="space-y-3">
            {data?.results.map((doc) => (
              <div key={doc.id} className="flex items-center gap-4 p-4 border border-gray-100 rounded-lg hover:bg-gray-50">
                <FileText size={24} className="text-red-400 shrink-0" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">{doc.title}</p>
                  <p className="text-xs text-gray-500">
                    {formatBytes(doc.file_size)} · {doc.page_count} pages ·{' '}
                    {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                  {doc.error_message && (
                    <p className="text-xs text-red-500 mt-1">{doc.error_message}</p>
                  )}
                </div>
                <Badge variant={statusVariant[doc.status] ?? 'default'}>
                  {doc.status}
                </Badge>
                <button
                  onClick={() => {
                    if (window.confirm('Delete this document?')) {
                      deleteMutation.mutate(doc.id);
                    }
                  }}
                  className="text-gray-400 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default DocumentsPage;
