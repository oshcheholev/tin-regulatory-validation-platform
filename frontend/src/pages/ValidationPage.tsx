import React, { useState, useRef, useMemo } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { validationService, ruleService } from '@/services';
import { Card, Button, Badge } from '@/components/common';
import { CheckSquare, Upload, AlertCircle, CheckCircle } from 'lucide-react';
import toast from 'react-hot-toast';
import type { ValidationResult } from '@/types';
import Select from 'react-select';

const ValidationPage: React.FC = () => {
  const [country, setCountry] = useState('');
  const [tin, setTin] = useState('');
  const [result, setResult] = useState<ValidationResult | null>(null);
  const [batchName, setBatchName] = useState('');
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const queryClient = useQueryClient();

  const { data: countries } = useQuery({
    queryKey: ['countries'],
    queryFn: () => ruleService.listCountries(),
  });

  const validateMutation = useMutation({
    mutationFn: () => validationService.validate({ country: country.toUpperCase(), tin }),
    onSuccess: (data) => {
      setResult(data);
      queryClient.invalidateQueries({ queryKey: ['validation-results'] });
    },
    onError: () => toast.error('Validation failed. Please try again.'),
  });

  const batchMutation = useMutation({
    mutationFn: (formData: FormData) => validationService.uploadBatch(formData),
    onSuccess: () => {
      toast.success('Batch uploaded! Processing in background...');
      setBatchName('');
      setBatchFile(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
      queryClient.invalidateQueries({ queryKey: ['batches'] });
    },
    onError: () => toast.error('Batch upload failed'),
  });

  const handleValidate = (e: React.FormEvent) => {
    e.preventDefault();
    if (!country || !tin) {
      toast.error('Please enter a country code and TIN');
      return;
    }
    setResult(null);
    validateMutation.mutate();
  };

  const handleBatchUpload = (e: React.FormEvent) => {
    e.preventDefault();
    if (!batchFile || !batchName.trim()) {
      toast.error('Please provide a name and CSV file');
      return;
    }
    const formData = new FormData();
    formData.append('name', batchName.trim());
    formData.append('csv_file', batchFile);
    batchMutation.mutate(formData);
  };

  const countryOptions = useMemo(() => {
    if (!countries) return [];
    return countries.map(c => ({
      value: c.code,
      label: `${c.code} – ${c.name}`
    }));
  }, [countries]);

  const selectedCountry = countryOptions.find(opt => opt.value === country) || null;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Validate TIN</h1>
        <p className="text-gray-500 mt-1">Validate a Tax Identification Number against OECD rules</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Single validation */}
        <Card title="Single TIN Validation">
          <form onSubmit={handleValidate} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Country *</label>
              <Select
                options={countryOptions}
                value={selectedCountry}
                onChange={(option) => setCountry(option?.value || '')}
                placeholder="Select or type country..."
                isClearable
                isSearchable
                className="text-sm"
                styles={{
                  control: (base) => ({
                    ...base,
                    borderRadius: '0.5rem',
                    borderColor: '#D1D5DB',
                    minHeight: '42px',
                    '&:hover': {
                      borderColor: '#D1D5DB'
                    }
                  })
                }}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">TIN *</label>
              <input
                type="text"
                value={tin}
                onChange={(e) => setTin(e.target.value)}
                placeholder="Enter TIN number"
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <Button type="submit" isLoading={validateMutation.isPending} className="w-full">
              <CheckSquare size={16} className="mr-2" />
              Validate TIN
            </Button>
          </form>

          {/* Result display */}
          {result && (
            <div className={`mt-6 p-4 rounded-xl border-2 ${result.is_valid ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}>
              <div className="flex items-center gap-3 mb-3">
                {result.is_valid ? (
                  <CheckCircle size={24} className="text-green-600" />
                ) : (
                  <AlertCircle size={24} className="text-red-500" />
                )}
                <div>
                  <p className="font-semibold text-gray-900">
                    {result.is_valid ? '✓ Valid TIN' : '✗ Invalid TIN'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {result.country_name} ({result.country_code})
                  </p>
                </div>
                <Badge variant={result.is_valid ? 'success' : 'error'} className="ml-auto">
                  {result.status}
                </Badge>
              </div>
              <pre className="text-xs text-gray-700 whitespace-pre-wrap font-sans leading-relaxed">
                {result.explanation}
              </pre>
              {result.matched_rules.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-medium text-gray-600 mb-2">Matched Rules:</p>
                  <div className="space-y-1">
                    {result.matched_rules.map((rule) => (
                      <div key={rule.id} className="flex items-center gap-2 text-xs text-gray-600">
                        <CheckCircle size={12} className="text-green-500" />
                        {rule.description}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* Batch validation */}
        <Card title="Batch CSV Validation">
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-xs text-blue-700 font-medium">CSV Format</p>
            <p className="text-xs text-blue-600 mt-1">Required columns: <code className="font-mono">country,tin</code></p>
            <p className="text-xs text-blue-500 mt-1 font-mono">US,123-45-6789<br />GB,1234567890</p>
          </div>
          <form onSubmit={handleBatchUpload} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Batch Name *</label>
              <input
                type="text"
                value={batchName}
                onChange={(e) => setBatchName(e.target.value)}
                placeholder="e.g. Q1 2024 Customer TINs"
                className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">CSV File *</label>
              <div
                className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-primary-400 transition-colors cursor-pointer"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload size={20} className="mx-auto text-gray-400 mb-2" />
                {batchFile ? (
                  <p className="text-sm text-gray-700">{batchFile.name}</p>
                ) : (
                  <p className="text-sm text-gray-500">Click to select CSV file</p>
                )}
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".csv"
                  className="hidden"
                  onChange={(e) => setBatchFile(e.target.files?.[0] ?? null)}
                />
              </div>
            </div>
            <Button type="submit" isLoading={batchMutation.isPending} className="w-full" variant="secondary">
              <Upload size={16} className="mr-2" />
              Upload & Process Batch
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default ValidationPage;
