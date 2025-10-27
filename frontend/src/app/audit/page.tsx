'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import DashboardLayout from '@/components/templates/DashboardLayout';
import Input from '@/components/atoms/Input';
import Button from '@/components/atoms/Button';
import Loader from '@/components/atoms/Loader';
import Badge from '@/components/atoms/Badge';
import { FiDownload, FiCheckCircle, FiXCircle, FiAlertTriangle } from 'react-icons/fi';
import toast from 'react-hot-toast';

interface SEOCheck {
  name: string;
  status: string;
  value?: string;
  recommendation?: string;
}

interface SEOCategory {
  category: string;
  checks: SEOCheck[];
}

interface SEOIssue {
  priority: string;
  issue: string;
  recommendation: string;
}

interface AuditResult {
  url: string;
  overall_score: number;
  issues_to_fix: SEOIssue[];
  common_issues: SEOCategory[];
}

export default function AuditPage() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AuditResult | null>(null);
  const [auditId, setAuditId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url) return;

    setLoading(true);
    try {
      const response = await fetch('/api/v1/audit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) throw new Error('Audit failed');

      const data = await response.json();
      setResult(data);
      setAuditId(data.audit_id); // Use audit ID for download
      toast.success('SEO audit completed!');
    } catch (error) {
      toast.error('Failed to complete audit');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!auditId) return;
    
    try {
      const response = await fetch(`/api/v1/audit/${auditId}/download`);
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `seo-audit-${Date.now()}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      toast.success('Report downloaded successfully!');
    } catch (error) {
      toast.error('Failed to download report');
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass': return <FiCheckCircle className="w-4 h-4 text-green-500" />;
      case 'fail': return <FiXCircle className="w-4 h-4 text-red-500" />;
      default: return <FiAlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <DashboardLayout
      title="SEO Audit Tool"
      description="Comprehensive SEO analysis with Core Web Vitals, performance metrics, and actionable recommendations."
    >
      <div className="max-w-4xl mx-auto space-y-8">
        {/* URL Input Form */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="url"
              placeholder="https://example.com"
              label="Website URL"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
              disabled={loading}
            />
            <Button type="submit" loading={loading} className="w-full">
              {loading ? 'Analyzing...' : 'Start SEO Audit'}
            </Button>
          </form>
        </div>

        {/* Loading State */}
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-lg border border-gray-200 p-8 text-center"
          >
            <Loader size="lg" className="mx-auto mb-4 text-blue-600" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">Analyzing Website</h3>
            <p className="text-gray-600">
              Running comprehensive SEO audit including Core Web Vitals, performance metrics, and technical analysis...
            </p>
          </motion.div>
        )}

        {/* Results */}
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            {/* Score Overview */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900">SEO Audit Results</h2>
                  <p className="text-gray-600">{result.url}</p>
                </div>
                <div className="text-right">
                  <div className={`text-4xl font-bold ${getScoreColor(result.overall_score)}`}>
                    {result.overall_score}/100
                  </div>
                  <p className="text-sm text-gray-500">Overall Score</p>
                </div>
              </div>
              
              <Button onClick={handleDownload} className="inline-flex items-center gap-2">
                <FiDownload className="w-4 h-4" />
                Download PDF Report
              </Button>
            </div>

            {/* Issues to Fix */}
            {result.issues_to_fix.length > 0 && (
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h3 className="text-lg font-medium text-gray-900">Issues to Fix</h3>
                  <p className="text-sm text-gray-500">Priority issues that need attention</p>
                </div>
                <div className="divide-y divide-gray-200">
                  {result.issues_to_fix.map((issue, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3, delay: index * 0.1 }}
                      className="px-6 py-4"
                    >
                      <div className="flex items-start gap-3">
                        <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${getPriorityColor(issue.priority)}`}>
                          {issue.priority.toUpperCase()}
                        </span>
                        <div className="flex-1">
                          <h4 className="font-medium text-gray-900">{issue.issue}</h4>
                          <p className="text-sm text-gray-600 mt-1">{issue.recommendation}</p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>
            )}

            {/* SEO Checklist */}
            <div className="space-y-4">
              <h3 className="text-xl font-semibold text-gray-900">SEO Checklist</h3>
              {result.common_issues.map((category, categoryIndex) => (
                <motion.div
                  key={category.category}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: categoryIndex * 0.1 }}
                  className="bg-white rounded-lg border border-gray-200 overflow-hidden"
                >
                  <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
                    <h4 className="font-medium text-gray-900">{category.category}</h4>
                  </div>
                  <div className="divide-y divide-gray-200">
                    {category.checks.map((check, checkIndex) => (
                      <div key={checkIndex} className="px-6 py-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          {getStatusIcon(check.status)}
                          <span className="font-medium text-gray-900">{check.name}</span>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-gray-600">{check.value}</div>
                          {check.recommendation && (
                            <div className="text-xs text-gray-500 mt-1">{check.recommendation}</div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </div>
    </DashboardLayout>
  );
}