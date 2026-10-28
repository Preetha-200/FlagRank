import { useMemo, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useResearchData } from '../lib/useResearchData';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ScatterChart, Scatter, ZAxis } from 'recharts';
import { Database, Activity, Target, ArrowRight } from 'lucide-react';
import { getApiUrl } from '../lib/config';

export function Dashboard() {
  const { data, metadata, loading, error, setUploadedResult, resetData } = useResearchData();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [uploadError, setUploadError] = useState<string>('');
  const [isUploading, setIsUploading] = useState(false);
  
  const rowsPerPage = 15;

  // Memoize visualizations and table data
  const { scatterData, deviationDist, scoreDist, topCandidates } = useMemo(() => {
    if (!data.length) return { scatterData: [], deviationDist: [], scoreDist: [], topCandidates: [] };

    // Scatter: Observed vs Expected
    // We only take a sample to avoid overcrowding the scatter plot
    const scatter = data.map(d => ({
      x: d.amazon_rank,
      y: d.expected_rank,
      z: d.suspiciousness_score,
      id: d.asin
    }));

    // Deviation Dist (Histogram-like)
    const devBins = Array(20).fill(0).map((_, i) => ({ bin: -50 + i * 5, count: 0 }));
    data.forEach(d => {
      const dev = d.rank_deviation;
      const binIdx = Math.max(0, Math.min(19, Math.floor((dev + 50) / 5)));
      if (devBins[binIdx]) devBins[binIdx].count++;
    });

    // Score Dist
    const scoreBins = Array(20).fill(0).map((_, i) => ({ bin: i * 5, count: 0 }));
    data.forEach(d => {
      const score = d.suspiciousness_score;
      const binIdx = Math.max(0, Math.min(19, Math.floor(score / 5)));
      if (scoreBins[binIdx]) scoreBins[binIdx].count++;
    });

    // Top candidates sorted by suspiciousness
    const sorted = [...data].sort((a, b) => b.suspiciousness_score - a.suspiciousness_score);

    return { scatterData: scatter, deviationDist: devBins, scoreDist: scoreBins, topCandidates: sorted };
  }, [data]);

  if (loading) return <div className="p-8 text-[#3A6F75]">Loading research dataset...</div>;
  if (error) return <div className="p-8 text-red-500">Error: {error}</div>;
  

  const totalPages = Math.ceil(topCandidates.length / rowsPerPage);
  
  let page = parseInt(searchParams.get('candidatePage') || '1', 10);
  if (isNaN(page) || page < 1) page = 1;
  if (totalPages > 0 && page > totalPages) page = totalPages;

  const handlePageChange = (newPage: number) => {
    setSearchParams(prev => {
      const next = new URLSearchParams(prev);
      next.set('candidatePage', newPage.toString());
      return next;
    });
  };

  const currentTableData = topCandidates.slice((page - 1) * rowsPerPage, page * rowsPerPage);

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setUploadError('');
    setUploadStatus('Starting analysis...');
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
      const response = await fetch(getApiUrl('/api/analyze'), {
        method: 'POST',
        body: formData,
      });
      
      if (!response.ok) {
        let errStr = 'Upload failed';
        try {
          const errData = await response.json();
          errStr = errData.detail || errStr;
        } catch {
          // ignore parsing error and keep default error string
        }
        throw new Error(errStr);
      }
      
      if (!response.body) throw new Error("No response body");
      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      
      let buffer = "";
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";
        
        for (const line of lines) {
          if (!line.trim()) continue;
          const parsed = JSON.parse(line);
          
          if (parsed.error) {
            throw new Error(parsed.error);
          }
          if (parsed.status) {
            setUploadStatus(parsed.status);
          }
          if (parsed.result) {
            setUploadedResult(parsed.result.data, parsed.result.metadata);
            setUploadStatus('');
          }
        }
      }
    } catch (err: any) {
      setUploadError(err.message);
      setUploadStatus('');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="mb-8 flex justify-between items-start">
        <div>
          <h1 className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41] mb-2">Research Dashboard</h1>
          <p className="font-['Alef'] text-[18px] text-[#1E5B5C]">Overview of the ranking inconsistency dataset and expected-ranking baseline.</p>
        </div>
      </div>

      {/* Upload Section */}
      <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-sm mb-[40px]">
        <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium text-[#1E5B5C] mb-4">Upload Custom Dataset</h3>
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
          <input 
            type="file" 
            accept=".csv"
            onChange={e => { setFile(e.target.files?.[0] || null); setUploadError(''); }}
            className="text-sm font-['Alef'] text-[18px] text-[#1E5B5C] file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#E6F7FA] file:text-[#1E5B5C] hover:file:bg-[#B4D5DC]"
            disabled={isUploading}
          />
          <button
            onClick={handleUpload}
            disabled={!file || isUploading}
            className="px-4 py-2 bg-[#1E5B5C] text-white rounded-md text-sm font-medium hover:bg-[#1C3B41] disabled:opacity-50"
          >
            Run Analysis
          </button>
          <button
            onClick={() => { resetData(); setFile(null); setUploadStatus(''); setUploadError(''); }}
            disabled={isUploading}
            className="px-4 py-2 bg-[#E6F7FA] text-[#1C3B41] rounded-md text-sm font-medium hover:bg-[#B4D5DC] disabled:opacity-50"
          >
            Reset
          </button>
        </div>
        {uploadStatus && (
          <div className="mt-3 text-sm font-medium text-[#1E5B5C] flex items-center">
            <span className="w-2 h-2 rounded-full bg-[#1E5B5C] animate-pulse mr-2"></span>
            {uploadStatus}
          </div>
        )}
        {uploadError && (
          <div className="mt-3 text-sm font-medium text-red-600 border border-red-200 bg-red-50 p-2 rounded">
            Error: {uploadError}
          </div>
        )}
      </div>

      {/* Top Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
          <div className="flex items-center gap-2 mb-2 text-[#3A6F75]">
            <Database className="w-4 h-4" />
            <h3 className="font-['Alef'] text-[14px] font-bold uppercase tracking-wider text-[#3A6F75]">Dataset Overview</h3>
          </div>
          <div className="mt-4 grid grid-cols-2 gap-4">
            <div>
              <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? metadata.total_products.toLocaleString() : "--"}</p>
              <p className="font-['Alef'] text-[16px] text-[#3A6F75]">Products</p>
            </div>
            <div>
              <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? metadata.unique_queries : "--"}</p>
              <p className="font-['Alef'] text-[16px] text-[#3A6F75]">Queries</p>
            </div>
          </div>
        </div>

        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
          <div className="flex items-center gap-2 mb-2 text-[#3A6F75]">
            <Target className="w-4 h-4" />
            <h3 className="font-['Alef'] text-[14px] font-bold uppercase tracking-wider text-[#3A6F75]">Observed Rank Range</h3>
          </div>
          <div className="mt-4">
            <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? `${metadata.rank_min} to ${metadata.rank_max}` : "--"}</p>
            <p className="font-['Alef'] text-[16px] text-[#3A6F75]">Search position boundaries</p>
          </div>
        </div>

        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20] lg:col-span-2">
          <div className="flex items-center gap-2 mb-2 text-[#3A6F75]">
            <Activity className="w-4 h-4" />
            <h3 className="font-['Alef'] text-[14px] font-bold uppercase tracking-wider text-[#3A6F75]">Model Performance (5-fold grouped OOF evaluation)</h3>
          </div>
          <div className="mt-4 grid grid-cols-3 gap-4">
            <div>
              <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? metadata.oof_mae.toFixed(2) : "--"}</p>
              <p className="font-['Alef'] text-[16px] text-[#3A6F75]">MAE</p>
            </div>
            <div>
              <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? metadata.oof_rmse.toFixed(2) : "--"}</p>
              <p className="font-['Alef'] text-[16px] text-[#3A6F75]">RMSE</p>
            </div>
            <div>
              <p className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41]">{metadata ? metadata.oof_r2.toFixed(2) : "--"}</p>
              <p className="font-['Alef'] text-[16px] text-[#3A6F75]">R² (Variance Explained)</p>
            </div>
          </div>
        </div>
      </div>

      {metadata && (<>
      {/* Visualizations Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Scatter Plot */}
        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
          <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium text-[#1E5B5C] mb-2">Observed vs Expected Rank</h3>
          <p className="font-['Alef'] text-[16px] text-[#3A6F75] mb-6">Lower number = better placement. Points below the diagonal are ranked better than expected.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 10, bottom: 20, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis type="number" dataKey="x" name="Observed" label={{ value: 'Observed Rank', position: 'bottom', fontSize: 12 }} reversed />
                <YAxis type="number" dataKey="y" name="Expected" label={{ value: 'Expected Rank', angle: -90, position: 'insideLeft', fontSize: 12 }} reversed />
                <ZAxis type="number" dataKey="z" range={[20, 20]} />
                <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ fontSize: '12px' }} />
                <Scatter name="Products" data={scatterData} fill="#C2E2F0" fillOpacity={0.6} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
        

        {/* Deviation Distribution */}
        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
          <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium text-[#1E5B5C] mb-2">Rank Deviation Distribution</h3>
          <p className="font-['Alef'] text-[16px] text-[#3A6F75] mb-6">Negative = ranked better than expected. Positive = ranked worse than expected.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deviationDist} margin={{ top: 10, right: 10, bottom: 20, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="bin" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <RechartsTooltip contentStyle={{ fontSize: '12px' }} />
                <Bar dataKey="count" fill="#3A6F75" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Score Distribution */}
        <div className="bg-[#FFFFFF] p-[30px] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20]">
          <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium text-[#1E5B5C] mb-2">Suspiciousness Score Distribution</h3>
          <p className="font-['Alef'] text-[16px] text-[#3A6F75] mb-6">A relative ranking-inconsistency measure (0-100). Higher scores indicate greater structural anomaly.</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={scoreDist} margin={{ top: 10, right: 10, bottom: 20, left: -20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="bin" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <RechartsTooltip contentStyle={{ fontSize: '12px' }} />
                <Bar dataKey="count" fill="#B4D5DC" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Candidate Table */}
      <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-[0px_4px_4px_#B4D5DC/20] overflow-hidden mt-[40px]">
        <div className="px-[30px] py-[20px] border-b border-[#B4D5DC] bg-[#E6F7FA] flex justify-between items-center">
          <div>
            <h3 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium text-[#1E5B5C]">Highest-Scoring Candidates</h3>
            <p className="font-['Alef'] text-[16px] text-[#3A6F75]">Products sorted by their empirical relative ranking-inconsistency measure.</p>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="font-['Alef'] text-[16px] text-[#3A6F75] bg-[#E6F7FA] border-b border-[#B4D5DC] uppercase">
              <tr>
                <th className="px-4 py-3 font-semibold">ASIN</th>
                <th className="px-4 py-3 font-semibold max-w-xs">Query</th>
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
            <tbody className="divide-y divide-[#E6F7FA]">
              {currentTableData.map((row) => (
                <tr key={row.asin + row.query} className="hover:bg-[#E6F7FA]/50 transition-colors">
                  <td className="px-4 py-3 font-['Alan_Sans'] text-[#1C3B41]">{row.asin}</td>
                  <td className="px-4 py-3 font-['Alan_Sans'] text-[#1E5B5C] truncate max-w-xs" title={row.query}>{row.query}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] font-medium text-[#1E5B5C]">{row.amazon_rank}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] text-[#1E5B5C]">{row.expected_rank.toFixed(1)}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] text-[#1E5B5C]">{row.rank_deviation > 0 ? '+' : ''}{row.rank_deviation.toFixed(1)}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] text-[#1E5B5C]">{row.relative_rank_gap.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] text-[#1E5B5C]">{row.rank_inconsistency_z.toFixed(2)}</td>
                  <td className="px-4 py-3 text-right font-['Alan_Sans'] font-bold text-[#dc8400]">{row.suspiciousness_score.toFixed(1)}</td>
                  <td className="px-4 py-3 text-center">
                    {row.feat_sponsored === 1 ? (
                      <span className="inline-flex items-center justify-center w-[72px] py-1 rounded text-[10px] font-medium bg-[#B4D5DC] text-[#152D31]">Sponsored</span>
                    ) : (
                      <span className="inline-flex items-center justify-center w-[72px] py-1 rounded text-[10px] font-medium bg-[#E6F7FA] font-['Alef'] text-[#1E5B5C]">Organic</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <button 
                      onClick={() => navigate(`/product/${row.asin}?query=${encodeURIComponent(row.query)}`, { state: { product: row } })}
                      className="inline-flex items-center text-[#1E5B5C] hover:text-[#1C3B41] underline font-medium text-xs"
                    >
                      Analyze <ArrowRight className="w-3 h-3 ml-1" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-[30px] py-[20px] border-t border-[#B4D5DC] bg-[#FFFFFF] flex items-center justify-between flex-wrap gap-4">
          <span className="font-['Alef'] text-[16px] text-[#3A6F75]">
            Showing {(page - 1) * rowsPerPage + 1} to {Math.min(page * rowsPerPage, topCandidates.length)} of {topCandidates.length} entries
          </span>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <span className="font-['Alef'] text-[16px] text-[#3A6F75]">Page</span>
              <select 
                value={page}
                onChange={(e) => handlePageChange(Number(e.target.value))}
                className="text-xs border border-[#B4D5DC] rounded px-2 py-1 outline-none focus:border-[#1E5B5C] bg-white text-[#1C3B41]"
              >
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => (
                  <option key={p} value={p}>{p} of {totalPages}</option>
                ))}
              </select>
            </div>
            <div className="flex gap-1">
              <button 
                onClick={() => handlePageChange(Math.max(1, page - 1))}
                disabled={page === 1}
                className="px-3 py-1 border border-[#B4D5DC] rounded text-xs font-['Alef'] text-[18px] text-[#1E5B5C] disabled:opacity-50 hover:bg-[#E6F7FA]/50"
              >
                Previous
              </button>
              <button 
                onClick={() => handlePageChange(Math.min(totalPages, page + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border border-[#B4D5DC] rounded text-xs font-['Alef'] text-[18px] text-[#1E5B5C] disabled:opacity-50 hover:bg-[#E6F7FA]/50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
      </>)}
    </div>
  );
}