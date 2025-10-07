import DashboardLayout from '@/components/templates/DashboardLayout';
import Loader from '@/components/atoms/Loader';

export default function Loading() {
  return (
    <DashboardLayout
      title="Analysis Jobs"
      description="Monitor your SEO analysis jobs and access completed reports."
    >
      <div className="space-y-6">
        {/* Action Bar Skeleton */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse" />
            <div className="h-10 w-24 bg-gray-200 rounded-lg animate-pulse" />
          </div>
        </div>

        {/* Loading State */}
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader size="lg" className="mx-auto mb-4 text-blue-600" />
            <p className="text-gray-600">Loading your analysis jobs...</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}