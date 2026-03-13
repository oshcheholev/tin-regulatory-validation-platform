import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ruleService } from '@/services';
import { Card, Badge, Spinner, EmptyState } from '@/components/common';
import { BookOpen, Search } from 'lucide-react';
import type { Country } from '@/types';

const RulesPage: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState<string>('');
  const [search, setSearch] = useState('');

  const { data: countries, isLoading: countriesLoading } = useQuery({
    queryKey: ['countries'],
    queryFn: () => ruleService.listCountries(),
  });

  const { data: rules, isLoading: rulesLoading } = useQuery({
    queryKey: ['rules', selectedCountry, search],
    queryFn: () => {
      const params: Record<string, string> = {};
      if (selectedCountry) params.country = selectedCountry;
      if (search) params.search = search;
      return ruleService.listRules(params);
    },
  });

  const ruleTypeVariant: Record<string, 'info' | 'success' | 'warning' | 'default'> = {
    format: 'info',
    length: 'warning',
    checksum: 'success',
    structure: 'default',
    character_set: 'default',
    other: 'default',
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">TIN Validation Rules</h1>
        <p className="text-gray-500 mt-1">Extracted rules from OECD documents</p>
      </div>

      {/* Country chips */}
      <Card title="Countries">
        {countriesLoading ? (
          <Spinner />
        ) : (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCountry('')}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                selectedCountry === '' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              All ({countries?.count ?? 0})
            </button>
            {countries?.results.map((country: Country) => (
              <button
                key={country.code}
                onClick={() => setSelectedCountry(country.code)}
                className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                  selectedCountry === country.code
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {country.code} – {country.name} ({country.rule_count})
              </button>
            ))}
          </div>
        )}
      </Card>

      {/* Rules table */}
      <Card title={`Rules (${rules?.count ?? 0})`}>
        <div className="mb-4">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search rules..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="block w-full pl-9 pr-3 py-2 rounded-lg border border-gray-300 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>

        {rulesLoading ? (
          <div className="flex justify-center py-8">
            <Spinner />
          </div>
        ) : rules?.results.length === 0 ? (
          <EmptyState message="No rules found" icon={<BookOpen size={32} />} />
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Country</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Description</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Pattern</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Length</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {rules?.results.map((rule) => (
                  <tr key={rule.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3">
                      <div>
                        <span className="text-sm font-bold text-gray-900">{rule.country_code}</span>
                        <br />
                        <span className="text-xs text-gray-500">{rule.country_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={ruleTypeVariant[rule.rule_type] ?? 'default'}>
                        {rule.rule_type}
                      </Badge>
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-700 max-w-xs">
                      {rule.description}
                    </td>
                    <td className="px-4 py-3 text-xs font-mono text-gray-600 max-w-[200px] truncate">
                      {rule.regex_pattern || '–'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {rule.min_length != null || rule.max_length != null
                        ? `${rule.min_length ?? '?'}–${rule.max_length ?? '?'}`
                        : '–'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {Math.round(rule.confidence_score * 100)}%
                    </td>
                    <td className="px-4 py-3">
                      <Badge variant={rule.is_active ? 'success' : 'default'}>
                        {rule.is_active ? 'Active' : 'Inactive'}
                      </Badge>
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

export default RulesPage;
