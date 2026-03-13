import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { validationService, reportService } from '@/services';
import { Card, Badge, Button, Spinner, EmptyState } from '@/components/common';
import { ClipboardList, Download, RefreshCw } from 'lucide-react';
import toast from 'react-hot-toast';

const ResultsPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data: results, isLoading: resultsLoading, refetch } = useQuery({
    queryKey: ['validation-results'],
    queryFn: () => validationService.listResults(),
  });

  const { data: batches, isLoading: batchesLoading } = useQuery({
    queryKey: ['batches'],
    queryFn: () => validationService.listBatches(),
    refetchInterval: 5000,
  });

  const reportMutation = useMutation({
    mutationFn: (params: { format: 'csv' | 'json'; name: string }) =>
      reportService.generate(params),
    onSuccess: (report) => {
      toast.success('Report generated!');
      queryClient.invalidateQueries({ queryKey: ['reports'] });
      // Download immediately
      const url = reportService.getDownloadUrl(report.id);
      const token = localStorage.getItem('access_token');
      fetch(url, { headers: { Authorization: `Bearer ${token}` } })
        .then((r) => r.blob())
        .then((blob) => {
          const link = document.createElement('a');
          link.href = URL.createObjectURL(blob);
          link.download = report.name + '.' + report.format;
          link.click();
        });
    },
    onError: () => toast.error('Failed to generate report'),
  });

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Validation Results</h1>
          <p className="text-gray-500 mt-1">History of all TIN validations and batch jobs</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => refetch()} size="sm">
            <RefreshCw size={14} className="mr-1" />
            Refresh
          </Button>
          <Button
            size="sm"
            onClick={() => reportMutation.mutate({ format: 'csv', name: `report-${Date.now()}` })}
            isLoading={reportMutation.isPending}
          >
            <Download size={14} className="mr-1" />
            Export CSV
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => reportMutation.mutate({ format: 'json', name: `report-${Date.now()}` })}
            isLoading={reportMutation.isPending}
          >
            <Download size={14} className="mr-1" />
            Export JSON
          </Button>
        </div>
      </div>

      {/* Batches */}
      <Card title={`Batch Jobs (${batches?.count ?? 0})`}>
        {batchesLoading ? (
          <Spinner />
        ) : batches?.results.length === 0 ? (
          <EmptyState message="No batch jobs yet" />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Valid</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Invalid</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {batches?.results.map((batch) => (
                  <tr key={batch.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{batch.name}</td>
                    <td className="px-4 py-3">
                      <Badge variant={
                        batch.status === 'completed' ? 'success' :
                        batch.status === 'failed' ? 'error' :
                        'warning'
                      }>
                        {batch.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700">{batch.total_count}</td>
                    <td className="px-4 py-3 text-sm text-green-600">{batch.valid_count}</td>
                    <td className="px-4 py-3 text-sm text-red-500">{batch.invalid_count}</td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(batch.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      {batch.status === 'completed' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => reportMutation.mutate({
                            format: 'csv',
                            name: `batch-${batch.id}-report`,
                          })}
                        >
                          <Download size={12} className="mr-1" />
                          Export
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Individual results */}
      <Card title={`Individual Validations (${results?.count ?? 0})`}>
        {resultsLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : results?.results.length === 0 ? (
          <EmptyState message="No validations yet" icon={<ClipboardList size={32} />} />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Country</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">TIN</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {results?.results.map((result) => (
                  <tr key={result.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm text-gray-700">{result.country_code} – {result.country_name}</td>
                    <td className="px-4 py-3 text-sm font-mono text-gray-900">{result.tin}</td>
                    <td className="px-4 py-3">
                      <Badge variant={result.is_valid ? 'success' : 'error'}>
                        {result.status}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-xs text-gray-500">
                      {new Date(result.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ResultsPage;
