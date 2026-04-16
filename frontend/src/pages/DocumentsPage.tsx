import React, { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService, ruleService } from '@/services';
import { Card, Button, Badge, Spinner, EmptyState, Pagination } from '@/components/common';
import { Upload, FileText, Trash2, RefreshCw, DownloadCloud, AlertTriangle, Eye, X, Link as LinkIcon, BookOpen } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Document, TinRule } from '@/types';

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
  const [selectedTextDoc, setSelectedTextDoc] = useState<Document | null>(null);
  const [selectedRulesDoc, setSelectedRulesDoc] = useState<Document | null>(null);
  const [page, setPage] = useState(1);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documents', page],
    queryFn: () => documentService.list({ page: page.toString() }),
    refetchInterval: 5000, // Poll every 5s for status updates
  });

  const { data: syncStatus, refetch: refetchSync } = useQuery({
    queryKey: ['oecdSyncStatus'],
    queryFn: () => documentService.getSyncStatus(),
    refetchInterval: 3000,
  });

  const syncMutation = useMutation({
    mutationFn: () => documentService.syncOECD(),
    onSuccess: () => {
      toast.success('OECD sync started!');
      refetchSync();
    },
    onError: (err: any) => {
      if (err.response?.data?.status === 'already_running') {
        toast.error('Sync is already running');
      } else {
        toast.error('Failed to start sync');
      }
    }
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
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => syncMutation.mutate()} isLoading={syncMutation.isPending} size="sm">
            <DownloadCloud size={14} className="mr-1" />
            Sync OECD Updates
          </Button>
          <Button variant="outline" onClick={() => { refetch(); refetchSync(); }} size="sm">
            <RefreshCw size={14} className="mr-1" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Sync status card */}
      {syncStatus && (syncStatus.status === 'running' || syncStatus.total_found > 0) && (
        <Card title="OECD Synchronization Status">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div className="flex gap-6">
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Status</p>
                <div className="flex items-center mt-1">
                  {syncStatus.status === 'running' && <Spinner className="w-4 h-4 mr-2" />}
                  <span className="font-medium capitalize text-gray-900">{syncStatus.status}</span>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Found PDFs</p>
                <p className="text-gray-900 font-medium mt-1">{syncStatus.total_found}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Downloaded</p>
                <p className="text-gray-900 font-medium mt-1">{syncStatus.downloaded_count}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Errors</p>
                <p className={`font-medium mt-1 ${syncStatus.error_count > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                  {syncStatus.error_count}
                </p>
              </div>
            </div>
            {Object.keys(syncStatus.error_details || {}).length > 0 && (
              <div className="bg-red-50 text-red-800 text-sm p-3 rounded-lg flex-1 max-h-32 overflow-y-auto">
                <p className="font-semibold mb-1 flex items-center gap-1">
                  <AlertTriangle size={14} /> Download Errors:
                </p>
                <ul className="list-disc pl-5 space-y-1">
                  {Object.entries(syncStatus.error_details).map(([country, err]) => (
                    <li key={country}>
                      <strong>{country}:</strong> {String(err)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </Card>
      )}

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
      <Card title={
        <div className="flex justify-between items-center w-full pr-4">
          <span>Documents ({data?.count ?? 0})</span>
          {data?.status_counts && (
            <div className="flex gap-4 text-sm font-normal">
              <span className="text-green-600">Completed: {data.status_counts.completed}</span>
              <span className="text-red-600">Failed: {data.status_counts.failed}</span>
              <span className="text-blue-600">Processing: {data.status_counts.processing}</span>
              <span className="text-gray-500">Pending: {data.status_counts.pending}</span>
            </div>
          )}
        </div>
      }>
        {isLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : data?.results?.length === 0 ? (
          <EmptyState message="No documents uploaded yet" icon={<FileText size={32} />} />
        ) : (
          <div className="space-y-4">
            <div className="space-y-3">
              {data?.results?.map((doc: any) => (
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
                  {doc.file_url && (
                    <a
                      href={doc.file_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1 text-gray-400 hover:text-blue-500 transition-colors ml-2"
                      title="Download PDF"
                    >
                      <LinkIcon size={16} />
                    </a>
                  )}
                  {doc.rules_count > 0 && (
                    <button
                      onClick={() => setSelectedRulesDoc(doc)}
                      className="p-1 text-gray-400 hover:text-green-500 transition-colors ml-2"
                      title="View Extracted Rules"
                    >
                      <BookOpen size={16} />
                    </button>
                  )}
                  {doc.extracted_text && (
                    <button
                      onClick={() => setSelectedTextDoc(doc)}
                      className="p-1 text-gray-400 hover:text-blue-500 transition-colors ml-2"
                      title="View Extracted Text"
                    >
                      <Eye size={16} />
                    </button>
                  )}
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
            {data?.count > 25 && (
              <div className="pt-4 border-t border-gray-100">
                <Pagination 
                  currentPage={page} 
                  count={data.count} 
                  pageSize={25} 
                  onPageChange={setPage} 
                />
              </div>
            )}
          </div>
        )}
      </Card>

      {/* Modal for Text */}
      {selectedTextDoc && (
        <div className="fixed inset-0 z-50 flex justify-center items-center p-4 sm:p-8">
          <div className="absolute inset-0 bg-black/50" onClick={() => setSelectedTextDoc(null)}></div>
          <div className="relative bg-white rounded-lg shadow-xl flex flex-col w-full max-w-4xl max-h-full overflow-hidden z-10">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">
                Extracted Text: {selectedTextDoc.title}
              </h3>
              <button
                onClick={() => setSelectedTextDoc(null)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto flex-1 bg-gray-50 bg-opacity-50">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap font-mono p-4 bg-white border border-gray-200 rounded-lg">
                {selectedTextDoc.extracted_text || 'No text extracted.'}
              </pre>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Rules */}
      {selectedRulesDoc && (
        <RulesModal
          document={selectedRulesDoc}
          onClose={() => setSelectedRulesDoc(null)}
        />
      )}
    </div>
  );
};

interface RulesModalProps {
  document: Document;
  onClose: () => void;
}

const RulesModal: React.FC<RulesModalProps> = ({ document, onClose }) => {
  const { data: rulesData, isLoading } = useQuery({
    queryKey: ['rules-by-document', document.id],
    queryFn: () => ruleService.listRulesByDocument(document.id),
  });

  return (
    <div className="fixed inset-0 z-50 flex justify-center items-center p-4 sm:p-8">
      <div className="absolute inset-0 bg-black/50" onClick={onClose}></div>
      <div className="relative bg-white rounded-lg shadow-xl flex flex-col w-full max-w-4xl max-h-full overflow-hidden z-10">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Extracted Rules: {document.title}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-6 overflow-y-auto flex-1 bg-gray-50 bg-opacity-50">
          {isLoading ? (
            <div className="flex justify-center py-8">
              <Spinner />
            </div>
          ) : rulesData?.results.length === 0 ? (
            <EmptyState message="No rules extracted for this document" icon={<BookOpen size={32} />} />
          ) : (
            <div className="space-y-4">
              {rulesData?.results.map((rule: TinRule) => (
                <div key={rule.id} className="p-4 bg-white border border-gray-200 rounded-lg">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="info">{rule.country_code}</Badge>
                        <Badge variant={rule.is_active ? 'success' : 'default'}>
                          {rule.rule_type}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-900 font-medium">{rule.description}</p>
                      {rule.regex_pattern && (
                        <p className="text-xs text-gray-500 mt-2 font-mono bg-gray-50 p-2 rounded">
                          {rule.regex_pattern}
                        </p>
                      )}
                      {(rule.min_length !== null || rule.max_length !== null) && (
                        <p className="text-xs text-gray-500 mt-1">
                          Length: {rule.min_length ?? 0} - {rule.max_length ?? '∞'}
                        </p>
                      )}
                    </div>
                    <div className="text-right">
                      <p className="text-xs text-gray-500">Confidence</p>
                      <p className="text-sm font-medium text-gray-900">{(rule.confidence_score * 100).toFixed(0)}%</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DocumentsPage;
