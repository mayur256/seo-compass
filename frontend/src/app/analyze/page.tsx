import DashboardLayout from '@/components/templates/DashboardLayout';
import URLSubmissionForm from '@/components/molecules/URLSubmissionForm';
import { FiInfo, FiClock, FiCheckCircle } from 'react-icons/fi';

const steps = [
  {
    icon: FiInfo,
    title: 'Submit URL',
    description: 'Enter your website URL to start the analysis',
  },
  {
    icon: FiClock,
    title: 'Processing',
    description: 'Our AI analyzes competitors, keywords, and content (30-60 seconds)',
  },
  {
    icon: FiCheckCircle,
    title: 'Get Results',
    description: 'Download comprehensive SEO report with actionable insights',
  },
];

export default function AnalyzePage() {
  return (
    <DashboardLayout
      title="Start SEO Analysis"
      description="Enter your website URL to begin comprehensive SEO analysis with competitor research and content generation."
    >
      <div className="max-w-4xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12">
          {/* Form Section */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg border border-gray-200 p-8 shadow-sm">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">
                Website Analysis
              </h2>
              <URLSubmissionForm />
            </div>

            {/* Info Box */}
            <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-3">
                What You'll Get
              </h3>
              <ul className="space-y-2 text-blue-800">
                <li className="flex items-start gap-2">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>Top 5 competitor analysis with traffic estimates</span>
                </li>
                <li className="flex items-start gap-2">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>Keyword research with search volume and difficulty</span>
                </li>
                <li className="flex items-start gap-2">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>AI-generated content drafts for key pages</span>
                </li>
                <li className="flex items-start gap-2">
                  <FiCheckCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
                  <span>Downloadable CSV reports and content files</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Process Steps */}
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-900">
              How It Works
            </h2>
            
            <div className="space-y-6">
              {steps.map((step, index) => {
                const Icon = step.icon;
                return (
                  <div key={step.title} className="flex gap-4">
                    <div className="flex-shrink-0">
                      <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                        <Icon className="w-5 h-5 text-blue-600" />
                      </div>
                    </div>
                    <div>
                      <h3 className="text-lg font-medium text-gray-900 mb-1">
                        {index + 1}. {step.title}
                      </h3>
                      <p className="text-gray-600">
                        {step.description}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

            {/* Timing Info */}
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <h3 className="text-lg font-medium text-gray-900 mb-3">
                Processing Time
              </h3>
              <div className="space-y-2 text-sm text-gray-600">
                <p>• <strong>Typical Analysis:</strong> 30-60 seconds</p>
                <p>• <strong>Complex Sites:</strong> 1-2 minutes</p>
                <p>• <strong>Large Competitor Sets:</strong> 2-3 minutes</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}