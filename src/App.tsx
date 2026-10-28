import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { ResearchProvider } from './lib/useResearchData';

// Pages
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { RankingAnalysis } from './pages/RankingAnalysis';
import { ProductAnalysis } from './pages/ProductAnalysis';
import { ResearchEvaluation } from './pages/ResearchEvaluation';

function App() {
  return (
    <ResearchProvider>
      <Router>
        <Routes>
          {/* Landing Page without standard Layout */}
          <Route path="/" element={<Landing />} />
          
          {/* Main App with standard Layout */}
          <Route element={<Layout />}>
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="ranking" element={<RankingAnalysis />} />
            <Route path="product/:id" element={<ProductAnalysis />} />
            <Route path="evaluation" element={<ResearchEvaluation />} />
          </Route>
          
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ResearchProvider>
  );
}

export default App;
