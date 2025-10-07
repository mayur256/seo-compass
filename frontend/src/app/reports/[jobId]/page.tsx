import Link from 'next/link';
import { notFound } from 'next/navigation';
import { api } from '@/lib/api';
import { AnalysisReport, AnalysisJob } from '@/types';
import DashboardLayout from '@/components/templates/DashboardLayout';
import ReportSection from '@/components/organisms/ReportSection';
import DownloadSection from '@/components/organisms/DownloadSection';
import Badge from '@/components/atoms/Badge';
import Button from '@/components/atoms/Button';
import { FiArrowLeft, FiExternalLink } from 'react-icons/fi';

interface ReportPageProps {
  params: Promise<{ jobId: string }>;
}

async function getJobAndReport(jobId: string): Promise<{ job: AnalysisJob; report: AnalysisReport } | null> {
  try {
    const [job, report] = await Promise.all([
      api.getJob(jobId),
      api.getReport(jobId),
    ]);
    
    if (!job || !report) return null;
    
    return { job, report };
  } catch (error) {
    console.error('Failed to fetch job and report:', error);
    return null;
  }
}

export default async function ReportPage({ params }: ReportPageProps) {
  const { jobId } = await params;
  const data = await getJobAndReport(jobId);
  
  if (!data) {
    notFound();
  }
  
  const { job, report } = data;
  
  if (job.status !== 'COMPLETED') {
    return (
      <DashboardLayout
        title="Analysis In Progress"
        description="Your SEO analysis is still being processed."
      >
        <div className="max-w-2xl mx-auto text-center py-12">
          <div className="mb-6">
            <Badge status={job.status} className="text-base px-4 py-2" />
          </div>
          
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Analysis {job.status === 'IN_PROGRESS' ? 'In Progress' : 'Queued'}
          </h2>
          
          <p className="text-gray-600 mb-8">
            {job.status === 'IN_PROGRESS' 
              ? 'We\'re analyzing your website and competitors. This usually takes 30-60 seconds.'
              : 'Your analysis is queued and will start processing shortly.'
            }
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <Link href="/jobs">
              <Button variant="outline">
                <FiArrowLeft className="w-4 h-4 mr-2" />
                Back to Jobs
              </Button>
            </Link>
            
            <Button onClick={() => window.location.reload()}>
              Refresh Status
            </Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-4 mb-4">
              <Link href="/jobs">
                <Button variant="outline" size="sm">
                  <FiArrowLeft className="w-4 h-4 mr-2" />
                  Back to Jobs
                </Button>
              </Link>
              <Badge status={job.status} />
            </div>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              SEO Analysis Report
            </h1>
            
            <div className="flex items-center gap-2 text-gray-600">
              <span>Website:</span>
              <a
                href={job.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium inline-flex items-center gap-1"
              >
                {job.url}
                <FiExternalLink className="w-4 h-4" />
              </a>
            </div>
            
            <p className="text-sm text-gray-500 mt-2">
              Completed: {new Date(job.completed_at!).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Download Section */}
        <DownloadSection jobId={jobId} />

        {/* Report Content */}
        <ReportSection report={report} />
      </div>
    </DashboardLayout>
  );
}