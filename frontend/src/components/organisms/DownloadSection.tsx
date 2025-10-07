'use client';

import { useState } from 'react';
import Button from '@/components/atoms/Button';
import { downloadReport } from '@/actions/analysis';
import toast from 'react-hot-toast';
import { FiDownload, FiPackage } from 'react-icons/fi';
import { motion } from 'framer-motion';

interface DownloadSectionProps {
  jobId: string;
}

const DownloadSection = ({ jobId }: DownloadSectionProps) => {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = async () => {
    setIsDownloading(true);
    
    try {
      const result = await downloadReport(jobId);
      
      if (result.error) {
        toast.error(result.error);
        return;
      }

      if (result.blob) {
        // Create download link
        const url = window.URL.createObjectURL(result.blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `seo-report-${jobId.slice(0, 8)}.zip`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        
        toast.success('Report downloaded successfully!');
      }
    } catch (error) {
      toast.error('Failed to download report');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200 p-6"
    >
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <FiPackage className="w-6 h-6 text-blue-600" />
          </div>
        </div>
        
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Download Complete Report
          </h3>
          <p className="text-gray-600 mb-4">
            Get the full analysis package including CSV files for competitors and keywords, 
            plus all content drafts in a convenient ZIP file.
          </p>
          
          <div className="text-sm text-gray-500 mb-4">
            <p>📦 Package includes:</p>
            <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
              <li>competitors.csv - Competitor analysis data</li>
              <li>keywords.csv - Keyword research results</li>
              <li>content-drafts/ - AI-generated content files</li>
              <li>report-metadata.json - Analysis summary</li>
            </ul>
          </div>
          
          <Button
            onClick={handleDownload}
            loading={isDownloading}
            className="inline-flex items-center gap-2"
          >
            <FiDownload className="w-4 h-4" />
            {isDownloading ? 'Preparing Download...' : 'Download ZIP Report'}
          </Button>
        </div>
      </div>
    </motion.div>
  );
};

export default DownloadSection;