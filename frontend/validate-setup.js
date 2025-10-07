#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating SEO Compass Frontend Setup...\n');

const requiredFiles = [
  'package.json',
  'next.config.ts',
  'tsconfig.json',
  '.env.local',
  'src/app/layout.tsx',
  'src/app/page.tsx',
  'src/app/analyze/page.tsx',
  'src/app/jobs/page.tsx',
  'src/app/reports/[jobId]/page.tsx',
  'src/components/atoms/Button.tsx',
  'src/components/atoms/Input.tsx',
  'src/components/atoms/Badge.tsx',
  'src/components/atoms/Loader.tsx',
  'src/components/molecules/URLSubmissionForm.tsx',
  'src/components/molecules/JobStatusCard.tsx',
  'src/components/molecules/KeywordTable.tsx',
  'src/components/molecules/CompetitorList.tsx',
  'src/components/organisms/AnalysisDashboard.tsx',
  'src/components/organisms/ReportSection.tsx',
  'src/components/organisms/DownloadSection.tsx',
  'src/components/templates/DashboardLayout.tsx',
  'src/lib/api.ts',
  'src/types/index.ts',
  'src/actions/analysis.ts',
  'src/actions/jobs.ts',
];

const requiredDependencies = [
  'next',
  'react',
  'react-dom',
  'framer-motion',
  'react-icons',
  'react-hot-toast',
  'typescript',
  'tailwindcss',
];

let allValid = true;

// Check files
console.log('📁 Checking required files...');
requiredFiles.forEach(file => {
  const filePath = path.join(__dirname, file);
  if (fs.existsSync(filePath)) {
    console.log(`✅ ${file}`);
  } else {
    console.log(`❌ ${file} - MISSING`);
    allValid = false;
  }
});

// Check package.json dependencies
console.log('\n📦 Checking dependencies...');
try {
  const packageJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'package.json'), 'utf8'));
  const allDeps = { ...packageJson.dependencies, ...packageJson.devDependencies };
  
  requiredDependencies.forEach(dep => {
    if (allDeps[dep]) {
      console.log(`✅ ${dep} - ${allDeps[dep]}`);
    } else {
      console.log(`❌ ${dep} - MISSING`);
      allValid = false;
    }
  });
} catch (error) {
  console.log('❌ Could not read package.json');
  allValid = false;
}

// Check environment variables
console.log('\n🔧 Checking environment configuration...');
const envPath = path.join(__dirname, '.env.local');
if (fs.existsSync(envPath)) {
  const envContent = fs.readFileSync(envPath, 'utf8');
  if (envContent.includes('NEXT_PUBLIC_API_BASE_URL')) {
    console.log('✅ NEXT_PUBLIC_API_BASE_URL configured');
  } else {
    console.log('❌ NEXT_PUBLIC_API_BASE_URL not found in .env.local');
    allValid = false;
  }
} else {
  console.log('❌ .env.local file missing');
  allValid = false;
}

// Final result
console.log('\n' + '='.repeat(50));
if (allValid) {
  console.log('🎉 All checks passed! Frontend setup is complete.');
  console.log('\n🚀 To start development:');
  console.log('   pnpm dev');
  console.log('\n📖 Visit: http://localhost:3000');
} else {
  console.log('❌ Some checks failed. Please review the missing items above.');
  process.exit(1);
}