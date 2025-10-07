'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import Button from '@/components/atoms/Button';
import DashboardLayout from '@/components/templates/DashboardLayout';
import { FiTarget, FiUsers, FiSearch, FiFileText, FiTrendingUp, FiZap } from 'react-icons/fi';

const features = [
  {
    icon: FiUsers,
    title: 'Competitor Analysis',
    description: 'Discover top 5 ranking competitors with traffic estimates and keyword insights.',
  },
  {
    icon: FiSearch,
    title: 'Keyword Research',
    description: 'Extract keywords with search volume and difficulty scores automatically.',
  },
  {
    icon: FiFileText,
    title: 'Content Generation',
    description: 'AI-generated, SEO-optimized content drafts for key pages.',
  },
  {
    icon: FiTrendingUp,
    title: 'Actionable Insights',
    description: 'Data-driven recommendations for SEO improvement and growth.',
  },
];

export default function HomePage() {
  return (
    <DashboardLayout>
      {/* Hero Section */}
      <div className="text-center py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-4 py-2 rounded-full text-sm font-medium mb-6">
            <FiZap className="w-4 h-4" />
            Automated SEO Analysis Platform
          </div>
          
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Transform Any URL Into a
            <span className="text-blue-600 block">Complete SEO Strategy</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            SEO Compass analyzes your website and competitors to deliver comprehensive 
            SEO insights, keyword research, and AI-generated content drafts in minutes.
          </p>
          
          <div className="flex items-center justify-center gap-4">
            <Link href="/analyze">
              <Button size="lg" className="px-8">
                <FiTarget className="w-5 h-5 mr-2" />
                Start SEO Analysis
              </Button>
            </Link>
            <Link href="/jobs">
              <Button variant="outline" size="lg" className="px-8">
                View Analysis Jobs
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Features Section */}
      <div className="py-16">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-center mb-12"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Everything You Need for SEO Success
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            From competitor analysis to content generation, get all the insights 
            you need to dominate search rankings.
          </p>
        </motion.div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.3 + index * 0.1 }}
                className="bg-white rounded-lg p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600">
                  {feature.description}
                </p>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* CTA Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.8 }}
        className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl p-12 text-center text-white"
      >
        <h2 className="text-3xl font-bold mb-4">
          Ready to Boost Your SEO?
        </h2>
        <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
          Join thousands of marketers who use SEO Compass to analyze competitors, 
          research keywords, and generate optimized content.
        </p>
        <Link href="/analyze">
          <Button size="lg" variant="secondary" className="px-8">
            Get Started Free
          </Button>
        </Link>
      </motion.div>
    </DashboardLayout>
  );
}