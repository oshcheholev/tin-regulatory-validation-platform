import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { documentService, ruleService, validationService } from '@/services';
import { Card, Badge, Spinner } from '@/components/common';
import { FileText, Globe, CheckSquare, ClipboardList } from 'lucide-react';

const StatCard: React.FC<{
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
  to: string;
}> = ({ label, value, icon, color, to }) => (
  <Link to={to}>
    <Card className="hover:shadow-md transition-shadow cursor-pointer">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-500">{label}</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className={`p-3 rounded-xl ${color}`}>{icon}</div>
      </div>
    </Card>
  </Link>
);

const DashboardPage: React.FC = () => {
  const { data: docs, isLoading: docsLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentService.list(),
  });

  const { data: countries, isLoading: countriesLoading } = useQuery({
    queryKey: ['countries'],
    queryFn: () => ruleService.listCountries(),
  });

  const { data: rules, isLoading: rulesLoading } = useQuery({
    queryKey: ['rules'],
    queryFn: () => ruleService.listRules(),
  });

  const { data: results, isLoading: resultsLoading } = useQuery({
    queryKey: ['validation-results'],
    queryFn: () => validationService.listResults(),
  });

  const isLoading = docsLoading || countriesLoading || rulesLoading || resultsLoading;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner />
      </div>
    );
  }

  const validCount = results?.results.filter((r) => r.is_valid).length ?? 0;
  const totalCount = results?.count ?? 0;
  const validRate = totalCount > 0 ? Math.round((validCount / totalCount) * 100) : 0;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 mt-1">Overview of your TIN validation platform</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
        <StatCard
          label="OECD Documents"
          value={docs?.count ?? 0}
          icon={<FileText size={24} className="text-blue-600" />}
          color="bg-blue-50"
          to="/documents"
        />
        <StatCard
          label="Countries Covered"
          value={countries?.length ?? 0}
          icon={<Globe size={24} className="text-purple-600" />}
          color="bg-purple-50"
          to="/rules"
        />
        <StatCard
          label="TIN Rules"
          value={rules?.count ?? 0}
          icon={<CheckSquare size={24} className="text-green-600" />}
          color="bg-green-50"
          to="/rules"
        />
        <StatCard
          label="Validations"
          value={totalCount}
          icon={<ClipboardList size={24} className="text-orange-600" />}
          color="bg-orange-50"
          to="/results"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Validation rate */}
        <Card title="Validation Success Rate">
          <div className="flex items-center gap-4">
            <div className="relative w-24 h-24">
              <svg viewBox="0 0 36 36" className="w-24 h-24 -rotate-90">
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#e5e7eb"
                  strokeWidth="3"
                />
                <path
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth="3"
                  strokeDasharray={`${validRate}, 100`}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-lg font-bold text-gray-900">{validRate}%</span>
              </div>
            </div>
            <div>
              <p className="text-sm text-gray-500">Out of {totalCount} validations</p>
              <p className="text-green-600 font-medium">{validCount} valid</p>
              <p className="text-red-500">{totalCount - validCount} invalid</p>
            </div>
          </div>
        </Card>

        {/* Recent documents */}
        <Card title="Recent Documents">
          {docs?.results.length === 0 ? (
            <p className="text-sm text-gray-500">No documents uploaded yet</p>
          ) : (
            <ul className="space-y-3">
              {docs?.results.slice(0, 5).map((doc) => (
                <li key={doc.id} className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 truncate max-w-[200px]">{doc.title}</span>
                  <Badge variant={doc.status === 'completed' ? 'success' : doc.status === 'failed' ? 'error' : 'warning'}>
                    {doc.status}
                  </Badge>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Recent validations */}
        <Card title="Recent Validations">
          {results?.results.length === 0 ? (
            <p className="text-sm text-gray-500">No validations yet. <Link to="/validate" className="text-primary-600 hover:underline">Validate a TIN</Link></p>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead>
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">TIN</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {results?.results.slice(0, 8).map((result) => (
                    <tr key={result.id}>
                      <td className="px-4 py-2 text-sm text-gray-700">{result.country_code}</td>
                      <td className="px-4 py-2 text-sm font-mono text-gray-900">{result.tin}</td>
                      <td className="px-4 py-2">
                        <Badge variant={result.is_valid ? 'success' : 'error'}>
                          {result.status}
                        </Badge>
                      </td>
                      <td className="px-4 py-2 text-xs text-gray-500">
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
    </div>
  );
};

export default DashboardPage;
