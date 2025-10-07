import { motion } from 'framer-motion';
import { Competitor } from '@/types';
import { FiExternalLink, FiTrendingUp } from 'react-icons/fi';

interface CompetitorListProps {
  competitors: Competitor[];
}

const CompetitorList = ({ competitors }: CompetitorListProps) => {
  const formatTraffic = (traffic: number) => {
    if (traffic >= 1000000) {
      return `${(traffic / 1000000).toFixed(1)}M`;
    }
    if (traffic >= 1000) {
      return `${(traffic / 1000).toFixed(1)}K`;
    }
    return traffic.toString();
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="bg-white rounded-lg border border-gray-200 overflow-hidden"
    >
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">Top Competitors</h3>
        <p className="text-sm text-gray-500">Websites ranking for similar keywords</p>
      </div>
      
      <div className="divide-y divide-gray-200">
        {competitors.map((competitor, index) => (
          <motion.div
            key={competitor.url}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
            className="px-6 py-4 hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="inline-flex items-center justify-center w-6 h-6 bg-blue-100 text-blue-800 text-xs font-medium rounded-full">
                    #{competitor.rank}
                  </span>
                  <a
                    href={competitor.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 font-medium truncate flex items-center gap-1"
                  >
                    {competitor.url.replace(/^https?:\/\//, '')}
                    <FiExternalLink className="w-3 h-3 flex-shrink-0" />
                  </a>
                </div>
                <p className="text-sm text-gray-600 truncate">
                  Keyword: <span className="font-medium">{competitor.keyword}</span>
                </p>
              </div>
              
              <div className="ml-4 text-right">
                <div className="flex items-center gap-1 text-green-600">
                  <FiTrendingUp className="w-4 h-4" />
                  <span className="text-sm font-medium">
                    {formatTraffic(competitor.estimated_traffic)}
                  </span>
                </div>
                <p className="text-xs text-gray-500">monthly visits</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
};

export default CompetitorList;