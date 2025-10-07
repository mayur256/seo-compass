# SEO Compass Frontend

Modern Next.js 14+ frontend with TypeScript, built using atomic design architecture to connect with the SEO Compass FastAPI backend.

## 🚀 Quick Start

```bash
# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

## 🏗️ Architecture

Built with **Atomic Design** principles:

```
src/
├── app/                    # Next.js App Router pages
│   ├── analyze/           # URL submission page
│   ├── jobs/              # Job listing page
│   ├── reports/[jobId]/   # Dynamic report pages
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Homepage
├── components/
│   ├── atoms/             # Basic UI elements
│   │   ├── Button.tsx     # Reusable button component
│   │   ├── Input.tsx      # Form input component
│   │   ├── Badge.tsx      # Status indicators
│   │   └── Loader.tsx     # Loading spinner
│   ├── molecules/         # Component combinations
│   │   ├── URLSubmissionForm.tsx
│   │   ├── JobStatusCard.tsx
│   │   ├── KeywordTable.tsx
│   │   └── CompetitorList.tsx
│   ├── organisms/         # Complex UI sections
│   │   ├── AnalysisDashboard.tsx
│   │   ├── ReportSection.tsx
│   │   └── DownloadSection.tsx
│   └── templates/         # Page layouts
│       └── DashboardLayout.tsx
├── actions/               # Server actions
├── lib/                   # Utilities and API client
├── types/                 # TypeScript interfaces
└── services/              # External service integrations
```

## 🎨 Tech Stack

- **Next.js 14+** - App Router with Server Components
- **TypeScript** - Type safety and developer experience
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations and transitions
- **React Icons** - Lightweight icon library
- **React Hot Toast** - Toast notifications
- **pnpm** - Fast, disk space efficient package manager

## 🔌 API Integration

Connects to FastAPI backend at `http://localhost:8000`:

- `POST /v1/analyze` - Submit URL for analysis
- `GET /v1/jobs` - List all analysis jobs
- `GET /v1/jobs/{jobId}` - Get job details
- `GET /v1/analyze/{jobId}` - Get analysis report
- `GET /v1/reports/{jobId}/download` - Download ZIP report

## 📱 Pages & Features

### Homepage (`/`)
- Hero section with feature overview
- Call-to-action buttons
- Responsive design with animations

### Analyze Page (`/analyze`)
- URL submission form with validation
- Process explanation
- Real-time form feedback

### Jobs Page (`/jobs`)
- Server-side rendered job listing
- Real-time status updates
- Refresh functionality
- Navigation to reports

### Report Page (`/reports/[jobId]`)
- Dynamic routing for job reports
- Competitor analysis tables
- Keyword research results
- Collapsible content drafts
- ZIP download functionality

## 🎯 Key Features

### Server Components First
- Maximizes performance with server-side rendering
- Reduces client-side JavaScript bundle
- SEO-friendly by default

### Server Actions
- Form submissions without client-side JavaScript
- Automatic revalidation and navigation
- Progressive enhancement

### Atomic Design
- Reusable, composable components
- Consistent design system
- Easy maintenance and testing

### Animations & UX
- Framer Motion for smooth transitions
- Loading states and skeletons
- Toast notifications for feedback
- Responsive design for all devices

## 🔧 Development

### Environment Variables

Create `.env.local`:

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Scripts

```bash
pnpm dev          # Development server with Turbopack
pnpm build        # Production build
pnpm start        # Production server
pnpm lint         # ESLint checking
```

### Component Development

Follow atomic design principles:

1. **Atoms** - Basic UI elements (buttons, inputs)
2. **Molecules** - Simple component groups (forms, cards)
3. **Organisms** - Complex UI sections (dashboards, reports)
4. **Templates** - Page layouts and structure

## 🚀 Deployment

The frontend is optimized for deployment on Vercel, Netlify, or any Node.js hosting platform:

```bash
# Build for production
pnpm build

# The output will be in the .next/ directory
```

## 🧪 Testing

```bash
# Run type checking
pnpm type-check

# Run linting
pnpm lint

# Run tests (when added)
pnpm test
```

## 📦 Bundle Analysis

```bash
# Analyze bundle size
pnpm analyze
```

## 🤝 Contributing

1. Follow atomic design principles
2. Use TypeScript for all components
3. Prefer server components over client components
4. Use server actions for form submissions
5. Add proper loading and error states
6. Ensure responsive design
7. Add meaningful animations with Framer Motion

---

**Built with ❤️ using Next.js 14+ and modern React patterns**