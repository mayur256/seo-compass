import Link from 'next/link';
import Badge from '@/components/atoms/Badge';
import Button from '@/components/atoms/Button';
import { AnalysisJob } from '@/types';
import { motion } from 'framer-motion';

interface JobStatusCardProps {
  job: AnalysisJob;
}

const JobStatusCard = ({ job }: JobStatusCardProps) => {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg border border-gray-200 p-6 shadow-sm hover:shadow-md transition-shadow"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 mb-2">
            <Badge status={job.status} />
            <span className="text-sm text-gray-500">
              ID: {job.job_id.slice(0, 8)}...
            </span>
          </div>
          
          <h3 className="text-lg font-medium text-gray-900 truncate mb-2">
            {job.url}
          </h3>
          
          <div className="text-sm text-gray-500 space-y-1">
            <p>Started: {formatDate(job.created_at)}</p>
            {job.completed_at && (
              <p>Completed: {formatDate(job.completed_at)}</p>
            )}
          </div>
        </div>
        
        <div className="ml-4">
          {job.status === 'COMPLETED' ? (
            <Link href={`/reports/${job.job_id}`}>
              <Button size="sm">View Report</Button>
            </Link>
          ) : (
            <Button size="sm" variant="outline" disabled>
              {job.status === 'IN_PROGRESS' ? 'Processing...' : 'Pending'}
            </Button>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export default JobStatusCard;