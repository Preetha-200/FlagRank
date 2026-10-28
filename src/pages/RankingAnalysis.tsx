import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useResearchData } from '../lib/useResearchData';
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Cell } from 'recharts';
import { Search, Filter, ArrowRight, Info } from 'lucide-react';

export function RankingAnalysis() {
  const { data, loading, error } = useResearchData();
  const navigate = useNavigate();
  
  const queries = useMemo(() => {
    const qs = Array.from(new Set(data.map(d => d.query)));
    return qs.sort();
  }, [data]);

  const [selectedQuery, setSelectedQuery] = useState<string>('');
  const [sponsoredFilter, setSponsoredFilter] = useState<'all' | 'sponsored' | 'organic'>('all');

  // Initialize selectedQuery once data is loaded
  useMemo(() => {
    if (queries.length > 0 && !selectedQuery) {
      setSelectedQuery(queries[0]);
    }
  }, [queries, selectedQuery]);

  const filteredData = useMemo(() => {
    if (!selectedQuery) return [];
    let qData = data.filter(d => d.query === selectedQuery);
    
    if (sponsoredFilter === 'sponsored') {
      qData = qData.filter(d => d.feat_sponsored === 1);
    } else if (sponsoredFilter === 'organic') {
      qData = qData.filter(d => d.feat_sponsored === 0);
    }
    
    return qData.sort((a, b) => a.amazon_rank - b.amazon_rank);
  }, [data, selectedQuery, sponsoredFilter]);

  const scatterData = useMemo(() => {
    return filteredData.map(d => ({
      x: d.amazon_rank,
      y: d.expected_rank,
      z: d.suspiciousness_score,
      id: d.asin,
      isSponsored: d.feat_sponsored === 1
    }));
  }, [filteredData]);

  if (loading) return <div className="p-8 font-['Alef'] text-[#3A6F75]">Loading research dataset...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;

  return (
    <div className="space-y-6 pb-12">
      <div className="mb-6">
        <h1 className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41] mb-2">Query-Level Ranking Analysis</h1>
        <p className="font-['Alef'] text-[#1E5B5C]">Inspect peer-group observed vs expected ranking behavior within isolated search queries.</p>
      </div>

      {/* Filters */}
      <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-sm flex flex-col md:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <label className="block text-xs font-semibold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Select Query</label>
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <select 
              value={selectedQuery} 
              onChange={(e) => setSelectedQuery(e.target.value)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {queries.map(q => <option key={q} value={q}>{q}</option>)}
            </select>
          </div>
        </div>

        <div className="w-full md:w-48">
          <label className="block text-xs font-semibold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Sponsorship</label>
          <div className="relative">
            <Filter className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <select 
              value={sponsoredFilter} 
              onChange={(e) => setSponsoredFilter(e.target.value as any)}
              className="w-full pl-9 pr-4 py-2 border border-slate-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Products</option>
              <option value="organic">Organic Only</option>
              <option value="sponsored">Sponsored Only</option>
            </select>
          </div>
        </div>
      </div>

      {/* Query Stats */}
      <div className="bg-[#1E5B5C] rounded-lg p-4 flex flex-col sm:flex-row gap-4 sm:items-center justify-between shadow-sm text-[#EEFFFF]">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#152D31] flex items-center justify-center font-bold text-white">
            {filteredData.length}
          </div>
          <div>
            <p className="text-sm font-medium text-[#B4D5DC]">Products in current view</p>
            <p className="font-semibold">{selectedQuery || 'No query selected'}</p>
          </div>
        </div>
        
        <div className="bg-[#152D31]/50 border border-[#3A6F75] rounded-md p-3 max-w-sm text-xs text-[#B4D5DC] flex items-start gap-2">
          <Info className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <p>
            <strong>Reminder:</strong> Lower numerical rank is better. 
            <span className="text-emerald-400 font-semibold block mt-1">Negative Deviation: Ranked better than expected.</span>
            <span className="text-orange-400 font-semibold block">Positive Deviation: Ranked worse than expected.</span>
          </p>
        </div>
      </div>

      {/* Visualization */}
      <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
        <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C] mb-1">Observed vs Expected Rank (Peer Group)</h3>
        <p className="text-xs font-['Alef'] text-[#3A6F75] mb-6">Visualizing relative displacement. Points exactly on the diagonal are ranked exactly as expected.</p>
        
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis type="number" dataKey="x" name="Observed Rank" label={{ value: 'Observed Rank (Lower is better ->)', position: 'bottom', fontSize: 12 }} reversed domain={['dataMax + 1', 0]} />
              <YAxis type="number" dataKey="y" name="Expected Rank" label={{ value: 'Expected Rank (Lower is better ->)', angle: -90, position: 'insideLeft', fontSize: 12 }} reversed domain={['dataMax + 2', 0]} />
              <RechartsTooltip 
                cursor={{ strokeDasharray: '3 3' }} 
                contentStyle={{ fontSize: '12px', borderRadius: '4px' }}
                formatter={(value: any, name: any) => [Number(value).toFixed(1), String(name)]}
              />
              <Scatter name="Products" data={scatterData}>
                {scatterData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.isSponsored ? '#f59e0b' : '#3b82f6'} fillOpacity={0.7} />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center gap-6 mt-4 text-xs font-medium font-['Alef'] text-[#1E5B5C]">
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-blue-500 opacity-70"></div> Organic</div>
          <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-full bg-amber-500 opacity-70"></div> Sponsored</div>
        </div>
      </div>

      {/* Query Table */}
      <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs font-['Alef'] text-[#3A6F75] bg-[#E6F7FA] border-b border-[#B4D5DC] uppercase">
              <tr>
                <th className="px-4 py-3 font-semibold">ASIN</th>
                <th className="px-4 py-3 font-semibold text-right">Observed</th>
                <th className="px-4 py-3 font-semibold text-right">Expected</th>
                <th className="px-4 py-3 font-semibold text-right">Deviation</th>
                <th className="px-4 py-3 font-semibold text-right">Rel Gap</th>
                <th className="px-4 py-3 font-semibold text-right">Inconsistency Z</th>
                <th className="px-4 py-3 font-semibold text-right">Suspiciousness</th>
                <th className="px-4 py-3 font-semibold text-center">Status</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredData.map((row) => (
                <tr key={row.asin} className="hover:bg-[#E6F7FA] transition-colors">
                  <td className="px-4 py-3 font-mono text-[#1C3B41]">{row.asin}</td>
                  <td className="px-4 py-3 text-right font-medium text-[#1C3B41]">{row.amazon_rank}</td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C]">{row.expected_rank.toFixed(1)}</td>
                  <td className="px-4 py-3 text-right font-medium">
                    <span className={row.rank_deviation < -5 ? 'text-emerald-600' : row.rank_deviation > 5 ? 'text-orange-600' : "font-['Alef'] text-[#1E5B5C]"}>
                      {row.rank_deviation > 0 ? '+' : ''}{row.rank_deviation.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C]">{row.relative_rank_gap.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C]">{row.rank_inconsistency_z.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-bold text-[#1C3B41]">{row.suspiciousness_score.toFixed(1)}</td>
                  <td className="px-4 py-3 text-center">
                    {row.feat_sponsored === 1 ? (
                      <span className="inline-flex items-center justify-center w-[72px] py-1 rounded text-[10px] font-medium bg-[#B4D5DC] text-[#152D31]">Sponsored</span>
                    ) : (
                      <span className="inline-flex items-center justify-center w-[72px] py-1 rounded text-[10px] font-medium bg-[#EEFFFF] font-['Alef'] text-[#1E5B5C]">Organic</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button 
                      onClick={() => navigate(`/product/${row.asin}?query=${encodeURIComponent(row.query)}`, { state: { product: row } })}
                      className="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium text-xs"
                    >
                      Analyze <ArrowRight className="w-3 h-3 ml-1" />
                    </button>
                  </td>
                </tr>
              ))}
              {filteredData.length === 0 && (
                <tr>
                  <td colSpan={9} className="px-4 py-8 text-center font-['Alef'] text-[#3A6F75]">
                    No products match the selected filters.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}