import DashboardLayout from '@/components/templates/DashboardLayout';
import Loader from '@/components/atoms/Loader';

export default function Loading() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header Skeleton */}
        <div className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="h-8 w-24 bg-gray-200 rounded-lg animate-pulse" />
            <div className="h-6 w-20 bg-gray-200 rounded-full animate-pulse" />
          </div>
          <div className="h-8 w-64 bg-gray-200 rounded-lg animate-pulse" />
          <div className="h-4 w-96 bg-gray-200 rounded-lg animate-pulse" />
        </div>

        {/* Download Section Skeleton */}
        <div className="bg-gray-100 rounded-lg p-6 animate-pulse">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-gray-200 rounded-lg" />
            <div className="flex-1 space-y-3">
              <div className="h-6 w-48 bg-gray-200 rounded" />
              <div className="h-4 w-full bg-gray-200 rounded" />
              <div className="h-4 w-3/4 bg-gray-200 rounded" />
              <div className="h-10 w-40 bg-gray-200 rounded-lg" />
            </div>
          </div>
        </div>

        {/* Loading State */}
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <Loader size="lg" className="mx-auto mb-4 text-blue-600" />
            <p className="text-gray-600">Loading analysis report...</p>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}