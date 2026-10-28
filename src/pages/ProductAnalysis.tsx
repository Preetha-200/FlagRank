import { useMemo, useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate, useLocation } from 'react-router-dom';
import { useResearchData } from '../lib/useResearchData';
import type { ResearchDataRow } from '../lib/useResearchData';
import { ArrowLeft, Box, Target, AlertCircle, Activity, Search } from 'lucide-react';
import { ResponsiveContainer, ComposedChart, Scatter, ScatterChart, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Cell, ReferenceLine, Bar } from 'recharts';

export function ProductAnalysis() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const queryParam = searchParams.get('query');
  const navigate = useNavigate();
  const { data, loading, error } = useResearchData();

  const [fallbackData, setFallbackData] = useState<ResearchDataRow[]>([]);
  const [fallbackMeta, setFallbackMeta] = useState<Record<string, Partial<ResearchDataRow>>>({});
  const [imageError, setImageError] = useState(false);

  // Safely decode the query parameter to resolve potential double-encoding or special chars like %
  const decodedQuery = useMemo(() => {
    if (!queryParam) return null;
    try {
      return decodeURIComponent(queryParam);
    } catch {
      return queryParam;
    }
  }, [queryParam]);

  // If the in-memory research data is empty (e.g. on page refresh or direct navigation), retrieve from research_data.json
  useEffect(() => {
    if (data.length === 0) {
      fetch('/research_data.json')
        .then(res => res.ok ? res.json() : [])
        .then((items: ResearchDataRow[]) => {
          if (Array.isArray(items) && items.length > 0) {
            setFallbackData(items);
          }
        })
        .catch(() => {});
    }
  }, [data.length]);

  // Reset image error state whenever product ID changes
  useEffect(() => {
    setImageError(false);
  }, [id]);

  const effectiveData = data.length > 0 ? data : fallbackData;

  const { rawProduct, peers } = useMemo(() => {
    const stateProduct = location.state?.product as ResearchDataRow | undefined;

    if (!effectiveData.length && stateProduct && stateProduct.asin === id) {
      return { rawProduct: stateProduct, peers: [stateProduct] };
    }

    if (!effectiveData.length || !id) return { rawProduct: null, peers: [] };

    // Find all records matching this ASIN
    const matches = effectiveData.filter(d => d.asin === id);
    if (!matches.length) {
      if (stateProduct && stateProduct.asin === id) {
        return { rawProduct: stateProduct, peers: [stateProduct] };
      }
      return { rawProduct: null, peers: [] };
    }

    // Match exact query with support for raw, decoded, and encoded forms to prevent cross-candidate mixing
    const p = matches.find(d => 
      d.query === queryParam || 
      (decodedQuery && d.query === decodedQuery) ||
      (queryParam && encodeURIComponent(d.query) === encodeURIComponent(queryParam))
    ) || matches[0];

    const peerGroup = effectiveData
      .filter(d => d.query === p.query)
      .sort((a, b) => a.amazon_rank - b.amazon_rank);

    return { rawProduct: p, peers: peerGroup };
  }, [effectiveData, id, queryParam, decodedQuery, location.state]);

  // If title or thumbnail is missing in rawProduct, retrieve matching product metadata from research_data.json
  useEffect(() => {
    if (!id) return;
    if (rawProduct?.title && rawProduct?.thumbnail) return;

    fetch('/research_data.json')
      .then(res => res.ok ? res.json() : [])
      .then((items: ResearchDataRow[]) => {
        if (!Array.isArray(items)) return;
        const match = items.find(d => d.asin === id && (d.query === queryParam || (decodedQuery && d.query === decodedQuery)))
                   || items.find(d => d.asin === id);
        if (match) {
          setFallbackMeta(prev => ({
            ...prev,
            [id]: match
          }));
        }
      })
      .catch(() => {});
  }, [id, rawProduct?.title, rawProduct?.thumbnail, queryParam, decodedQuery]);

  // Merge product data with any retrieved metadata
  const product = useMemo(() => {
    if (!rawProduct) return null;
    const meta = fallbackMeta[rawProduct.asin];
    if (!meta) return rawProduct;
    return {
      ...rawProduct,
      title: rawProduct.title || meta.title || null,
      thumbnail: rawProduct.thumbnail || meta.thumbnail || null,
      brand: rawProduct.brand || meta.brand || null,
      product_type: rawProduct.product_type || meta.product_type || null,
      color: rawProduct.color || meta.color || null,
      url: rawProduct.url || meta.url || null,
    };
  }, [rawProduct, fallbackMeta]);

  if (loading && !product) return <div className="p-8 font-['Alef'] text-[#3A6F75]">Loading research dataset...</div>;
  if (error && !product) return <div className="p-8 text-red-500">Error: {error}</div>;

  if (!product) {
    return (
      <div className="p-8 max-w-2xl mx-auto text-center mt-20">
        <AlertCircle className="w-12 h-12 text-[#B4D5DC] mx-auto mb-4" />
        <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C] mb-2">Product Not Found</h2>
        <p className="font-['Alef'] text-[#1E5B5C] mb-6">The requested identifier ({id}) was not found in the processed research dataset.</p>
        <button onClick={() => navigate(-1)} className="px-4 py-2 bg-[#EEFFFF] hover:bg-slate-200 text-slate-800 rounded-md font-medium text-sm transition-colors">
          Go Back
        </button>
      </div>
    );
  }

  const deviationDirection = product.rank_deviation < -0.5 ? 'better' : product.rank_deviation > 0.5 ? 'worse' : 'aligned';

  const chartData = [
    { name: 'Expected', rank: product.expected_rank },
    { name: 'Observed', rank: product.amazon_rank }
  ];

  const peerScatterData = peers.map(d => ({
    x: d.amazon_rank,
    y: d.expected_rank,
    z: d.suspiciousness_score,
    id: d.asin,
    isSelected: d.asin === product.asin
  }));

  return (
    <div className="space-y-6 pb-12">
      {/* Navigation */}
      <div className="flex items-center gap-4 mb-2">
        <button onClick={() => navigate(-1)} className="flex items-center text-sm font-medium font-['Alef'] text-[#3A6F75] hover:text-[#1C3B41] transition-colors">
          <ArrowLeft className="w-4 h-4 mr-1" /> Back
        </button>
      </div>

      {/* Header Overview */}
      <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20] flex flex-col md:flex-row gap-6 items-start">
        {product.thumbnail && !imageError ? (
          <div className="w-24 h-24 flex-shrink-0 bg-[#EEFFFF] rounded-md border border-[#B4D5DC] overflow-hidden flex items-center justify-center">
            <img 
              src={product.thumbnail} 
              alt={product.title || 'Product thumbnail'} 
              className="max-w-full max-h-full object-contain mix-blend-multiply"
              onError={() => setImageError(true)} 
            />
          </div>
        ) : (
          <div className="w-24 h-24 flex-shrink-0 bg-[#EEFFFF] rounded-md border border-[#B4D5DC] flex items-center justify-center text-slate-400">
            <Box className="w-8 h-8" />
          </div>
        )}
        
        <div className="flex-1">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#EEFFFF] font-['Alef'] text-[#1E5B5C] uppercase tracking-wider">{product.asin}</span>
            {product.feat_sponsored === 1 ? (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-blue-100 text-blue-800 uppercase tracking-wider">Sponsored</span>
            ) : (
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-100 text-emerald-800 uppercase tracking-wider">Organic</span>
            )}
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#EEFFFF] font-['Alef'] text-[#1E5B5C] uppercase tracking-wider">{product.category}</span>
          </div>
          <h1 className="font-['Alan_Sans',sans-serif] text-[24px] font-medium text-[#1E5B5C] mb-2 leading-tight">{product.title || 'Unknown Title'}</h1>
          <div className="text-sm font-['Alef'] text-[#1E5B5C] flex flex-wrap gap-x-6 gap-y-2">
            <p><strong className="text-[#1C3B41]">Query:</strong> {product.query}</p>
            {product.brand && <p><strong className="text-[#1C3B41]">Brand:</strong> {product.brand}</p>}
            {product.product_type && <p><strong className="text-[#1C3B41]">Type:</strong> {product.product_type}</p>}
          </div>
        </div>

        {/* Prominent Score */}
        <div className="w-full md:w-64 bg-[#E6F7FA] p-4 rounded-md border border-[#B4D5DC] text-center flex-shrink-0">
          <h3 className="text-xs font-bold font-['Alef'] text-[#3A6F75] uppercase tracking-widest mb-1">Suspiciousness Score</h3>
          <div className="text-4xl font-black tracking-tighter text-[#1C3B41] mb-1">
            {product.suspiciousness_score.toFixed(1)} <span className="text-lg text-slate-400 font-medium tracking-normal">/ 100</span>
          </div>
          <p className="text-[10px] font-['Alef'] text-[#3A6F75] uppercase tracking-wider font-semibold">Empirical relative ranking-inconsistency measure</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Column: Ranking Deviation & Interpretation */}
        <div className="lg:col-span-2 space-y-6">
          
          <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
            <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C] mb-6 flex items-center gap-2"><Target className="w-5 h-5 font-['Alef'] text-[#3A6F75]" /> Observed vs Expected Ranking</h2>
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
              <div className="bg-[#E6F7FA] p-3 rounded border border-[#B4D5DC] text-center">
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Observed Rank</p>
                <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{product.amazon_rank}</p>
              </div>
              <div className="bg-[#E6F7FA] p-3 rounded border border-[#B4D5DC] text-center">
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Expected Rank</p>
                <p className="text-2xl font-bold font-['Alef'] text-[#1E5B5C]">{product.expected_rank.toFixed(1)}</p>
              </div>
              <div className="bg-[#E6F7FA] p-3 rounded border border-[#B4D5DC] text-center md:col-span-1 col-span-2">
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Rank Deviation</p>
                <p className={`text-2xl font-bold ${product.rank_deviation < -5 ? 'text-emerald-600' : product.rank_deviation > 5 ? 'text-orange-600' : "font-['Alef'] text-[#1E5B5C]"}`}>
                  {product.rank_deviation > 0 ? '+' : ''}{product.rank_deviation.toFixed(1)}
                </p>
              </div>
              <div className="bg-[#E6F7FA] p-3 rounded border border-[#B4D5DC] text-center">
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Rel Gap</p>
                <p className="text-2xl font-bold font-['Alef'] text-[#1E5B5C]">{product.relative_rank_gap.toFixed(2)}</p>
              </div>
              <div className="bg-[#E6F7FA] p-3 rounded border border-[#B4D5DC] text-center">
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Z-Score</p>
                <p className="text-2xl font-bold font-['Alef'] text-[#1E5B5C]">{product.rank_inconsistency_z.toFixed(2)}</p>
              </div>
            </div>

            <div className="flex flex-col md:flex-row items-center gap-8">
              <div className="h-40 w-full md:w-1/2">
                <ResponsiveContainer width="100%" height="100%">
                  <ComposedChart layout="vertical" data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                    <XAxis type="number" reversed domain={[0, 'dataMax + 10']} label={{ value: 'Search Position (Lower is Better ->)', position: 'bottom', fontSize: 10 }} />
                    <YAxis type="category" dataKey="name" fontSize={12} fontWeight="bold" />
                    <RechartsTooltip cursor={{fill: '#f8fafc'}} contentStyle={{ fontSize: '12px' }} />
                    <Bar dataKey="rank" barSize={24} fill="#94a3b8">
                      {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.name === 'Observed' ? '#0f172a' : '#94a3b8'} />
                      ))}
                    </Bar>
                  </ComposedChart>
                </ResponsiveContainer>
              </div>
              <div className="flex-1 bg-blue-50 border border-blue-100 p-4 rounded-md text-sm text-blue-900 leading-relaxed">
                <h4 className="font-bold mb-1">Research Interpretation</h4>
                <p className="mb-2">
                  The product exhibits a <strong>{deviationDirection}</strong> observed ranking relative to the expected-ranking baseline.
                  Specifically, its observed rank is {Math.abs(product.rank_deviation).toFixed(1)} positions {deviationDirection} than expected.
                </p>
                <p>
                  This places the product {product.suspiciousness_score > 85 ? 'among the higher-scoring ranking-inconsistency candidates' : 'within a relatively normal discrepancy threshold'} for this query. The score is an empirical, dataset-relative measure and does not establish the cause of the ranking difference.
                </p>
              </div>
            </div>
          </div>

          {/* Observable Signals */}
          <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
            <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C] mb-4 flex items-center gap-2"><Activity className="w-5 h-5 font-['Alef'] text-[#3A6F75]" /> Observable Ranking Signals</h2>
            <p className="text-xs font-['Alef'] text-[#3A6F75] mb-6">These are the primary observable product signals contributing to the expected-ranking baseline. No single signal causally determines the ranking.</p>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-y-6 gap-x-4">
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Price</p>
                <p className="text-sm font-medium text-[#1C3B41]">${product.feat_price?.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Original Price</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_original_price ? `$${product.feat_original_price.toFixed(2)}` : 'N/A'}</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Savings</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_savings_percent ? `${product.feat_savings_percent.toFixed(0)}%` : '0%'}</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Rating</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_rating?.toFixed(1)} / 5.0</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Total Reviews (Log)</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_total_reviews_log?.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Title Length</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_title_length} chars</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Desc Length</p>
                <p className="text-sm font-medium text-[#1C3B41]">{product.feat_desc_length} chars</p>
              </div>
              <div>
                <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Brand Frequency</p>
                <p className="text-sm font-medium text-[#1C3B41]">{(product.feat_brand_freq * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Score Breakdown & Query Peers */}
        <div className="space-y-6">
          
          <div className="bg-[#1E5B5C] p-5 rounded-lg border border-slate-700 shadow-sm text-[#EEFFFF]">
            <h3 className="text-sm font-bold text-[#EEFFFF] mb-4 uppercase tracking-wider">Methodological Weighting</h3>
            <p className="text-xs text-slate-400 mb-4 leading-relaxed">
              The Suspiciousness Score is calculated using predefined methodological weighting choices on the absolute deviations. These are not learned probabilities.
            </p>
            
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-[#B4D5DC]">Absolute Inconsistency Z-Score</span>
                  <span className="font-bold">50%</span>
                </div>
                <div className="h-1.5 w-full bg-[#152D31] rounded-full overflow-hidden">
                  <div className="h-full bg-blue-400 w-1/2"></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-[#B4D5DC]">Absolute Relative Rank Gap</span>
                  <span className="font-bold">30%</span>
                </div>
                <div className="h-1.5 w-full bg-[#152D31] rounded-full overflow-hidden">
                  <div className="h-full bg-indigo-400" style={{ width: '30%' }}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-[#B4D5DC]">Absolute Rank Deviation</span>
                  <span className="font-bold">20%</span>
                </div>
                <div className="h-1.5 w-full bg-[#152D31] rounded-full overflow-hidden">
                  <div className="h-full bg-violet-400" style={{ width: '20%' }}></div>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
            <h3 className="text-sm font-bold text-[#1C3B41] mb-2 flex items-center gap-2"><Search className="w-4 h-4 font-['Alef'] text-[#3A6F75]" /> Query Peer Context</h3>
            <p className="text-xs font-['Alef'] text-[#3A6F75] mb-4">Comparing {peers.length} products returned for query: <span className="font-medium italic">"{product.query}"</span></p>
            
            <div className="h-48 mb-4">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis type="number" dataKey="x" reversed hide />
                  <YAxis type="number" dataKey="y" reversed hide />
                  <RechartsTooltip 
                    cursor={{ strokeDasharray: '3 3' }} 
                    contentStyle={{ fontSize: '10px', padding: '4px' }}
                    formatter={(val: any, name: any) => [Number(val).toFixed(1), String(name)]}
                  />
                  <ReferenceLine x={product.amazon_rank} stroke="#cbd5e1" strokeDasharray="3 3" />
                  <ReferenceLine y={product.expected_rank} stroke="#cbd5e1" strokeDasharray="3 3" />
                  <Scatter data={peerScatterData}>
                    {peerScatterData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.isSelected ? '#ef4444' : '#94a3b8'} r={entry.isSelected ? 6 : 4} />
                    ))}
                  </Scatter>
                </ScatterChart>
              </ResponsiveContainer>
              <p className="text-[10px] text-center text-slate-400 mt-1">Observed vs Expected (Red = Selected Product)</p>
            </div>

            <div className="max-h-64 overflow-y-auto pr-2 custom-scrollbar border-t border-slate-100 pt-2">
              <table className="w-full text-xs text-left">
                <thead className="font-['Alef'] text-[#3A6F75] sticky top-0 bg-white">
                  <tr>
                    <th className="py-2 font-medium">ASIN</th>
                    <th className="py-2 font-medium text-right">Obs</th>
                    <th className="py-2 font-medium text-right">Exp</th>
                    <th className="py-2 font-medium text-right">Score</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {peers.map((peer) => {
                    const isSelected = peer.asin === product.asin;
                    return (
                      <tr key={peer.asin} className={`transition-colors ${isSelected ? "bg-[#E6F7FA]" : "hover:bg-[#E6F7FA]/50"}`}>
                        <td className="py-2">
                          <button 
                            onClick={() => navigate(`/product/${peer.asin}?query=${encodeURIComponent(peer.query)}`, { state: { product: peer } })}
                            className={`font-mono transition-colors ${isSelected ? "font-bold text-[#1E5B5C]" : "font-['Alef'] text-[#1E5B5C] hover:text-[#1C3B41]"}`}
                          >
                            {peer.asin}
                          </button>
                        </td>
                        <td className={`py-2 text-right ${isSelected ? "font-bold text-[#1C3B41]" : "font-['Alef'] text-[#1E5B5C]"}`}>{peer.amazon_rank}</td>
                        <td className="py-2 text-right font-['Alef'] text-[#3A6F75]">{peer.expected_rank.toFixed(1)}</td>
                        <td className={`py-2 text-right ${isSelected ? "font-bold text-[#1C3B41]" : "font-medium text-[#1C3B41]"}`}>{peer.suspiciousness_score.toFixed(1)}</td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

          </div>

        </div>
      </div>
    </div>
  );
}