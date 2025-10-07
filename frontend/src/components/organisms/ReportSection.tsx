'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AnalysisReport, ContentDraft } from '@/types';
import KeywordTable from '@/components/molecules/KeywordTable';
import CompetitorList from '@/components/molecules/CompetitorList';
import { FiChevronDown, FiChevronRight, FiFileText } from 'react-icons/fi';

interface ReportSectionProps {
  report: AnalysisReport;
}

const ContentDraftCard = ({ draft }: { draft: ContentDraft }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full px-6 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FiFileText className="w-5 h-5 text-blue-600" />
            <h4 className="text-lg font-medium text-gray-900 capitalize">
              {draft.page_name} Page
            </h4>
          </div>
          {isExpanded ? (
            <FiChevronDown className="w-5 h-5 text-gray-400" />
          ) : (
            <FiChevronRight className="w-5 h-5 text-gray-400" />
          )}
        </div>
      </button>
      
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="border-t border-gray-200"
          >
            <div className="px-6 py-4">
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-mono bg-gray-50 p-4 rounded-lg overflow-x-auto">
                {draft.content}
              </pre>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

const ReportSection = ({ report }: ReportSectionProps) => {
  return (
    <div className="space-y-8">
      {/* Competitors Section */}
      {report.competitors && report.competitors.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <CompetitorList competitors={report.competitors} />
        </motion.div>
      )}

      {/* Keywords Section */}
      {report.keywords && report.keywords.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <KeywordTable keywords={report.keywords} />
        </motion.div>
      )}

      {/* Content Drafts Section */}
      {report.content_drafts && report.content_drafts.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
          className="space-y-4"
        >
          <div className="mb-6">
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Content Drafts</h3>
            <p className="text-gray-600">AI-generated content suggestions for your website</p>
          </div>
          
          <div className="space-y-4">
            {report.content_drafts.map((draft, index) => (
              <motion.div
                key={draft.page_name}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
              >
                <ContentDraftCard draft={draft} />
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
};

export default ReportSection;