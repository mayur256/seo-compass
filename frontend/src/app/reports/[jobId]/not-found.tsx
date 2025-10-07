import Link from 'next/link';
import DashboardLayout from '@/components/templates/DashboardLayout';
import Button from '@/components/atoms/Button';
import { FiArrowLeft, FiAlertCircle } from 'react-icons/fi';

export default function NotFound() {
  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto text-center py-16">
        <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
          <FiAlertCircle className="w-8 h-8 text-red-600" />
        </div>
        
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          Report Not Found
        </h1>
        
        <p className="text-lg text-gray-600 mb-8">
          The analysis report you're looking for doesn't exist or may have been removed.
        </p>
        
        <div className="flex items-center justify-center gap-4">
          <Link href="/jobs">
            <Button>
              <FiArrowLeft className="w-4 h-4 mr-2" />
              View All Jobs
            </Button>
          </Link>
          
          <Link href="/analyze">
            <Button variant="outline">
              Start New Analysis
            </Button>
          </Link>
        </div>
      </div>
    </DashboardLayout>
  );
}