import Link from 'next/link';
import { api } from '@/lib/api';
import { AnalysisJob } from '@/types';
import DashboardLayout from '@/components/templates/DashboardLayout';
import AnalysisDashboard from '@/components/organisms/AnalysisDashboard';
import Button from '@/components/atoms/Button';
import { refreshJobs } from '@/actions/jobs';
import { FiPlus, FiRefreshCw } from 'react-icons/fi';

async function getJobs(): Promise<AnalysisJob[]> {
  try {
    const jobs = await api.getJobs();
    return Array.isArray(jobs) ? jobs : [];
  } catch (error) {
    console.error('Failed to fetch jobs:', error);
    return [];
  }
}

export default async function JobsPage() {
  const jobs = await getJobs();

  return (
    <DashboardLayout
      title="Analysis Jobs"
      description="Monitor your SEO analysis jobs and access completed reports."
    >
      <div className="space-y-6">
        {/* Action Bar */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/analyze">
              <Button className="inline-flex items-center gap-2">
                <FiPlus className="w-4 h-4" />
                New Analysis
              </Button>
            </Link>
            
            <form action={refreshJobs}>
              <Button
                type="submit"
                variant="outline"
                className="inline-flex items-center gap-2"
              >
                <FiRefreshCw className="w-4 h-4" />
                Refresh
              </Button>
            </form>
          </div>
          
          {jobs.length > 0 && (
            <div className="text-sm text-gray-500">
              Last updated: {new Date().toLocaleTimeString()}
            </div>
          )}
        </div>

        {/* Jobs Dashboard */}
        <AnalysisDashboard jobs={jobs} />
      </div>
    </DashboardLayout>
  );
}