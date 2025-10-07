import { AnalysisJob } from '@/types';
import JobStatusCard from '@/components/molecules/JobStatusCard';
import Loader from '@/components/atoms/Loader';
import { motion } from 'framer-motion';

interface AnalysisDashboardProps {
  jobs: AnalysisJob[];
  loading?: boolean;
}

const AnalysisDashboard = ({ jobs, loading }: AnalysisDashboardProps) => {
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <Loader size="lg" className="mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading your analysis jobs...</p>
        </div>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center py-12"
      >
        <div className="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
          <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No analysis jobs yet</h3>
        <p className="text-gray-600 mb-6">Start your first SEO analysis to see results here.</p>
      </motion.div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900">Analysis Jobs</h2>
        <div className="text-sm text-gray-500">
          {jobs.length} {jobs.length === 1 ? 'job' : 'jobs'} total
        </div>
      </div>
      
      <div className="grid gap-4">
        {jobs.map((job, index) => (
          <motion.div
            key={job.job_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <JobStatusCard job={job} />
          </motion.div>
        ))}
      </div>
    </div>
  );
};

export default AnalysisDashboard;