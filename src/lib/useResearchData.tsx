import { useState, createContext, useContext } from 'react';
import type { ReactNode } from 'react';

export interface ResearchDataRow {
  query: string;
  category: string;
  feat_sponsored: number;
  amazon_rank: number;
  expected_rank: number;
  rank_deviation: number;
  absolute_rank_deviation: number;
  rank_inconsistency_z: number;
  relative_rank_gap: number;
  norm_inconsistency_z: number;
  norm_relative_gap: number;
  norm_rank_deviation: number;
  suspiciousness_score: number;
  asin: string;
  feat_discounted: number;
  feat_price: number;
  feat_original_price: number;
  feat_savings_percent: number;
  feat_rating: number;
  feat_total_reviews_log: number;
  feat_brand_freq: number;
  feat_title_length: number;
  feat_desc_length?: number;
  title: string | null;
  brand: string | null;
  product_type: string | null;
  color: string | null;
  url: string | null;
  thumbnail: string | null;
}

export interface ResearchMetadata {
  total_products: number;
  unique_queries: number;
  unique_asins: number;
  rank_min: number;
  rank_max: number;
  oof_mae: number;
  oof_rmse: number;
  oof_r2: number;
}

interface ResearchContextType {
  data: ResearchDataRow[];
  metadata: ResearchMetadata | null;
  loading: boolean;
  error: string | null;
  setUploadedResult: (data: ResearchDataRow[], metadata: ResearchMetadata) => void;
  resetData: () => void;
}

const ResearchContext = createContext<ResearchContextType | undefined>(undefined);

export function ResearchProvider({ children }: { children: ReactNode }) {
  const [data, setData] = useState<ResearchDataRow[]>([]);
  const [metadata, setMetadata] = useState<ResearchMetadata | null>(null);
  const loading = false;
  const [error, setError] = useState<string | null>(null);

  const setUploadedResult = (newData: ResearchDataRow[], newMetadata: ResearchMetadata) => {
    setData(newData);
    setMetadata(newMetadata);
  };

  const resetData = () => {
    setData([]);
    setMetadata(null);
    setError(null);
  };

  return (
    <ResearchContext.Provider value={{ data, metadata, loading, error, setUploadedResult, resetData }}>
      {children}
    </ResearchContext.Provider>
  );
}

export function useResearchData() {
  const context = useContext(ResearchContext);
  if (context === undefined) {
    throw new Error('useResearchData must be used within a ResearchProvider');
  }
  return context;
}
