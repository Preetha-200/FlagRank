import { Activity, Beaker, CheckCircle, Target, ShieldAlert } from 'lucide-react';

export function ResearchEvaluation() {
  const syntheticResults = [
    { id: 'S1', scenario: 'Upward +25% (Small)', targetCount: '44.0', roc: '0.3800 ± 0.049', pr: '0.0443 ± 0.006', rec50: '0.0431' },
    { id: 'S4', scenario: 'Downward -25% (Small)', targetCount: '43.8', roc: '0.4541 ± 0.041', pr: '0.0504 ± 0.006', rec50: '0.0425' },
    { id: 'S2', scenario: 'Upward +50% (Medium)', targetCount: '29.6', roc: '0.4798 ± 0.048', pr: '0.0403 ± 0.010', rec50: '0.0321' },
    { id: 'S5', scenario: 'Downward -50% (Medium)', targetCount: '28.7', roc: '0.4961 ± 0.052', pr: '0.0447 ± 0.009', rec50: '0.0773' },
    { id: 'S3', scenario: 'Upward +80% (Large)', targetCount: '12.3', roc: '0.7677 ± 0.063', pr: '0.0507 ± 0.021', rec50: '0.1924' },
    { id: 'S6', scenario: 'Downward -80% (Large)', targetCount: '12.0', roc: '0.7091 ± 0.076', pr: '0.0397 ± 0.019', rec50: '0.1672' },
  ];

  return (
    <div className="space-y-8 pb-12 max-w-5xl mx-auto">
      <div>
        <h1 className="font-['Alegreya_Sans_SC'] text-[32px] md:text-[40px] font-medium text-[#1C3B41] mb-2">Research Evaluation</h1>
        <p className="font-['Alef'] text-[#1E5B5C]">Review the actual framework validation results, robustness checks, and synthetic evaluation metrics.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Expected-Rank Model Validation */}
        <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Target className="w-5 h-5 text-blue-600" />
            <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">Internal grouped OOF framework validation</h2>
          </div>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-[#E6F7FA] p-3 rounded border border-slate-100 text-center">
              <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">MAE</p>
              <p className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">8.05</p>
              <p className="text-[11px] text-[#3A6F75]">Orig: 9.12 (-11.7%)</p>
            </div>
            <div className="bg-[#E6F7FA] p-3 rounded border border-slate-100 text-center">
              <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">RMSE</p>
              <p className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">10.49</p>
              <p className="text-[11px] text-[#3A6F75]">Orig: 12.08 (-13.2%)</p>
            </div>
            <div className="bg-[#E6F7FA] p-3 rounded border border-slate-100 text-center">
              <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">R²</p>
              <p className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">0.41</p>
              <p className="text-[11px] text-[#3A6F75]">Orig: 0.21 (+95.2%)</p>
            </div>
            <div className="bg-[#E6F7FA] p-3 rounded border border-slate-100 text-center">
              <p className="text-xs font-['Alef'] text-[#3A6F75] font-semibold uppercase tracking-wider mb-1">Spearman</p>
              <p className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">0.5553</p>
              <p className="text-[11px] text-[#3A6F75]">Orig: 0.4447 (+24.9%)</p>
            </div>
          </div>
          <p className="text-sm font-['Alef'] text-[#1E5B5C] leading-relaxed bg-blue-50 p-3 rounded-md text-blue-900 border border-blue-100">
            <strong>Interpretation:</strong> An R² of 0.4055 (MAE 8.05, Spearman 0.5553) reflects the Query-Relative Random Forest architecture evaluated via 5-fold grouped OOF cross-validation. By predicting normalized rank position y = (r - 1)/(N_q - 1) and scaling back using retrieved query list size N_q, the model overcomes query result length heterogeneity and outperforms the non-attribute Query Midpoint baseline (R² = 0.3902).
          </p>
        </div>

        {/* Suspiciousness Validation */}
        <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-sm p-6">
          <div className="flex items-center gap-2 mb-4">
            <Activity className="w-5 h-5 text-indigo-600" />
            <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">Suspiciousness score validation</h2>
          </div>
          
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <h3 className="text-xs font-bold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Distribution</h3>
              <ul className="text-sm text-[#1C3B41] space-y-1">
                <li className="flex justify-between border-b border-slate-100 py-1"><span>Minimum</span> <strong>≈ 2.44</strong></li>
                <li className="flex justify-between border-b border-slate-100 py-1"><span>Median</span> <strong>≈ 48.83</strong></li>
                <li className="flex justify-between border-b border-slate-100 py-1"><span>95th Pct</span> <strong>≈ 89.73</strong></li>
                <li className="flex justify-between py-1"><span>Maximum</span> <strong>≈ 99.86</strong></li>
              </ul>
            </div>
            <div>
              <h3 className="text-xs font-bold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Model Specifications</h3>
              <ul className="text-sm text-[#1C3B41] space-y-1">
                <li className="flex justify-between border-b border-slate-100 py-1"><span>Target Type</span> <strong>Query-Relative</strong></li>
                <li className="flex justify-between border-b border-slate-100 py-1"><span>Feature Count</span> <strong>12 (Pruned duplicate)</strong></li>
                <li className="flex justify-between border-b border-slate-100 py-1"><span>Ensemble</span> <strong>RF (300 trees, depth 6)</strong></li>
                <li className="flex justify-between py-1"><span>Score Bounds</span> <strong>[0.0, 100.0]</strong></li>
              </ul>
            </div>
          </div>
          <p className="text-xs font-['Alef'] text-[#3A6F75] leading-relaxed">
            Distribution across 1,094 records evaluated via Out-Of-Fold predictions. The scoring formula preserves the 50% / 30% / 20% weights combining standardized inconsistency Z-score, relative rank gap, and rank deviation.
          </p>
        </div>
      </div>

      {/* Synthetic Evaluation */}
      <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-sm overflow-hidden">
        <div className="p-6 border-b border-[#B4D5DC] bg-[#E6F7FA]">
          <div className="flex items-center gap-2 mb-2">
            <Beaker className="w-5 h-5 text-violet-600" />
            <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">Controlled Synthetic Evaluation</h2>
          </div>
          <p className="text-sm font-['Alef'] text-[#1E5B5C] mb-4 leading-relaxed">
            This section evaluates the framework&apos;s <strong>sensitivity to controlled rank perturbations</strong> introduced into observed rankings across 10 random seeds (42–51). 
            The production expected-rank model was not retrained using synthetic labels, and synthetic ground truth was strictly excluded from feature inputs.
          </p>
          <div className="flex items-start gap-2 bg-amber-50 p-3 rounded-md text-amber-900 border border-amber-200 text-sm">
            <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
            <p><strong>Strict Scientific Caveat:</strong> This is NOT real-world manipulation evidence. It does not establish real-world manipulation detection performance or accuracy. It strictly measures mathematical sensitivity to isolated structural rank shifts under controlled simulation assumptions.</p>
          </div>
        </div>

        <div className="overflow-x-auto p-6">
          <h3 className="text-sm font-bold text-[#1C3B41] mb-3">Perturbation Scenarios (Averaged over 10 random seeds, 42–51)</h3>
          <table className="w-full text-sm text-left border border-[#B4D5DC]">
            <thead className="text-xs font-['Alef'] text-[#3A6F75] bg-[#E6F7FA] uppercase border-b border-[#B4D5DC]">
              <tr>
                <th className="px-4 py-3 font-semibold border-r border-[#B4D5DC]">Scenario</th>
                <th className="px-4 py-3 font-semibold border-r border-[#B4D5DC]">Direction / Magnitude</th>
                <th className="px-4 py-3 font-semibold border-r border-[#B4D5DC] text-right">Avg Targets</th>
                <th className="px-4 py-3 font-semibold border-r border-[#B4D5DC] text-right">ROC-AUC (Mean ± Std)</th>
                <th className="px-4 py-3 font-semibold border-r border-[#B4D5DC] text-right">PR-AUC (Mean ± Std)</th>
                <th className="px-4 py-3 font-semibold text-right">Recall@50</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {syntheticResults.map((row) => (
                <tr key={row.id} className="hover:bg-[#E6F7FA]">
                  <td className="px-4 py-3 font-mono font-medium border-r border-[#B4D5DC]">{row.id}</td>
                  <td className="px-4 py-3 border-r border-[#B4D5DC]">{row.scenario}</td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C] border-r border-[#B4D5DC]">{row.targetCount}</td>
                  <td className="px-4 py-3 text-right font-medium text-[#1C3B41] border-r border-[#B4D5DC]">{row.roc}</td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C] border-r border-[#B4D5DC]">{row.pr}</td>
                  <td className="px-4 py-3 text-right font-['Alef'] text-[#1E5B5C]">{row.rec50}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-[10px] text-slate-400 mt-2 text-right">Note: Random baselines for PR-AUC equal positive target prevalence (~0.031 to ~0.047). S3 (ROC-AUC 0.7677) and S6 (ROC-AUC 0.7091) represent large structural perturbations where anomaly signals transcend marketplace noise.</p>
        </div>

        <div className="px-6 pb-6 pt-0">
          <div className="bg-[#EEFFFF] rounded-lg p-5">
            <h3 className="text-sm font-bold text-[#1C3B41] mb-2 flex items-center gap-2"><CheckCircle className="w-4 h-4 text-emerald-600" /> Synthetic Interpretation</h3>
            <ul className="list-disc pl-5 text-sm text-[#1C3B41] space-y-1">
              <li>Small perturbations (±25%) showed low separability (ROC-AUC ~0.38–0.45), overlapping substantially with organic marketplace variance.</li>
              <li>Medium perturbations (±50%) showed near-chance separability (ROC-AUC ~0.48–0.50).</li>
              <li>Large perturbations (±80%) achieved robust detection: <strong>Scenario S3 reached ROC-AUC 0.7677 ± 0.063</strong> (up from 0.7032) and <strong>Scenario S6 reached ROC-AUC 0.7091 ± 0.076</strong>.</li>
              <li>The query-relative model substantially strengthens the signal-to-noise ratio for large structural rank displacements.</li>
              <li><strong>It does not establish real-world manipulation detection performance</strong>, nor does it prove optimal binary thresholding against adversarial actors.</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Threshold Calibration & Flagging Rates */}
      <div className="bg-[#FFFFFF] rounded-[10px] border border-[#B4D5DC] shadow-sm p-6">
        <div className="flex items-center gap-2 mb-4">
          <ShieldAlert className="w-5 h-5 text-amber-600" />
          <h2 className="font-['Alegreya_Sans_SC'] text-[24px] font-medium font-['Alef'] text-[#1E5B5C]">Threshold Calibration &amp; Flagging Rates</h2>
        </div>
        <p className="text-sm font-['Alef'] text-[#1E5B5C] mb-4 leading-relaxed">
          Comparing candidate decision thresholds across the real-world dataset and the controlled Scenario S3 synthetic benchmark.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Real Dataset Flagging Rate */}
          <div className="border border-[#B4D5DC] rounded-lg p-4 bg-[#F8FAFC]">
            <h3 className="text-xs font-bold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Real Dataset Observed Flagging Rate</h3>
            <p className="text-xs text-[#3A6F75] mb-3">Total records: 1,094. No ground-truth manipulation labels exist on real data; values represent the empirical flagging prevalence (positive selection rate).</p>
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-[#B4D5DC] text-[#3A6F75]">
                  <th className="py-1">Threshold (τ)</th>
                  <th className="py-1 text-right">Flagged Products</th>
                  <th className="py-1 text-right">Observed Flagging Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 85</td><td className="text-right">94 / 1,094 (Top 15%: 164)</td><td className="text-right font-semibold">8.59% (14.99%)</td></tr>
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 92</td><td className="text-right">40 / 1,094 (Top 8%: 88)</td><td className="text-right font-semibold">3.66% (8.04%)</td></tr>
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 99</td><td className="text-right">4 / 1,094 (Top 1%: 11)</td><td className="text-right font-semibold">0.37% (1.01%)</td></tr>
              </tbody>
            </table>
          </div>

          {/* Synthetic Control FPR (Scenario S3) */}
          <div className="border border-[#B4D5DC] rounded-lg p-4 bg-[#F8FAFC]">
            <h3 className="text-xs font-bold font-['Alef'] text-[#3A6F75] uppercase tracking-wider mb-2">Synthetic Control FPR (Scenario S3: Large Upward Shift)</h3>
            <p className="text-xs text-[#3A6F75] mb-3">Measured strictly on unperturbed synthetic controls (synthetic_control == 1) across seeds 42–51. Evaluates false-alarm resistance under simulation.</p>
            <table className="w-full text-xs text-left">
              <thead>
                <tr className="border-b border-[#B4D5DC] text-[#3A6F75]">
                  <th className="py-1">Threshold (τ)</th>
                  <th className="py-1 text-right">Control FPR (Mean ± Std)</th>
                  <th className="py-1 text-right">Target Recall (Mean)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 85</td><td className="text-right font-semibold">9.85% ± 0.37%</td><td className="text-right">30.87%</td></tr>
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 92</td><td className="text-right font-semibold">4.37% ± 0.24%</td><td className="text-right">14.26%</td></tr>
                <tr><td className="py-1.5 font-mono font-medium">τ ≥ 99</td><td className="text-right font-semibold">0.39% ± 0.09%</td><td className="text-right">1.55%</td></tr>
              </tbody>
            </table>
          </div>
        </div>

        <div className="bg-amber-50 p-3 rounded-md text-amber-900 border border-amber-200 text-xs">
          <strong>Methodological Clarification:</strong> Real dataset flagging percentages must <em>never</em> be described as false-positive rates or verified error rates because unmanipulated ground-truth labels do not exist for commercial marketplace rankings. True false-positive rates can only be measured against defined negative controls within the controlled synthetic evaluation.
        </div>
      </div>

    </div>
  );
}
