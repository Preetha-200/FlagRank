import { Link, useLocation } from 'react-router-dom';
import { useEffect } from 'react';
import { Database, Filter, Layers, Calculator, GitMerge, AlertOctagon, BookOpen } from 'lucide-react';

export function Landing() {
  const { hash } = useLocation();

  useEffect(() => {
    if (hash === '#methodology') {
      const element = document.getElementById('methodology');
      if (element) {
        setTimeout(() => element.scrollIntoView({ behavior: 'smooth' }), 100);
      }
    }
  }, [hash]);
  const steps = [
    {
      id: 1,
      title: 'Stage 1: Observable Data',
      icon: Database,
      description: 'Ingestion of marketplace-observable product and ranking information, including price, reviews, categories, and query placement.'
    },
    {
      id: 2,
      title: 'Stage 2: Preprocessing',
      icon: Filter,
      description: 'Implementation of preprocessing safeguards including removal of zero-variance fields, preservation of valid zero ratings, handling of missing values, ensuring ranking continuity, and strictly avoiding target-based imputation.'
    },
    {
      id: 3,
      title: 'Stage 3: Feature Construction',
      icon: Layers,
      description: (
        <div className="mt-2">
          <p className="mb-4">Construction of 13 predictive features grouped into logical domains:</p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-[#f6fefd] p-4 rounded-xl border border-[#B4D5DC]">
              <span className="font-bold uppercase block mb-2 text-[#1E5B5C] text-sm">Numeric</span>
              <ul className="list-disc pl-6 space-y-1 text-[#1C3B41]">
                <li>Discounted status</li>
                <li>Sponsored status</li>
                <li>Price</li>
                <li>Original Price</li>
                <li>Savings Percentage</li>
                <li>Rating</li>
              </ul>
            </div>
            <div className="bg-[#f6fefd] p-4 rounded-xl border border-[#B4D5DC]">
              <span className="font-bold uppercase block mb-2 text-[#1E5B5C] text-sm">Text & Review</span>
              <ul className="list-disc pl-6 space-y-1 text-[#1C3B41]">
                <li>Log Total Reviews</li>
                <li>Title length</li>
                <li>Title/query overlap</li>
                <li>Description length</li>
              </ul>
            </div>
            <div className="bg-[#f6fefd] p-4 rounded-xl border border-[#B4D5DC] md:col-span-2">
              <span className="font-bold uppercase block mb-2 text-[#1E5B5C] text-sm">Categorical Frequency</span>
              <ul className="list-disc pl-6 space-y-1 text-[#1C3B41] flex flex-wrap gap-x-8">
                <li>Brand frequency</li>
                <li>Product type frequency</li>
                <li>Color frequency</li>
              </ul>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 4,
      title: 'Stage 4: Expected Ranking Model',
      icon: Calculator,
      description: 'A Random Forest Regressor is trained to estimate expected search positions using isolated 5-fold GroupKFold evaluation (isolating 44 query groups across 1,094 rows). The resulting Out-Of-Fold (OOF) predictions guarantee the baseline model has not seen the evaluated query during training.'
    },
    {
      id: 5,
      title: 'Stage 5: Peer Comparison',
      icon: GitMerge,
      description: 'A query-level evaluation comparing expected rank vs observed rank. Standardized metrics (rank deviation, query-relative z-score, relative rank gap) are calculated against the specific competing query peer-group. (Note: Current peer-group standardization retains self-inclusion as an identified methodological caveat).'
    },
    {
      id: 6,
      title: 'Stage 6: Suspiciousness Score',
      icon: AlertOctagon,
      description: 'Empirical calculation using a 50/30/20 weighting design on absolute normalized deviations to produce a final 0-100 relative inconsistency measure.'
    },
    {
      id: 7,
      title: 'Stage 7: Evaluation',
      icon: BookOpen,
      description: 'Validation utilizing internal grouped OOF metrics, score robustness checks across clipping bounds, and a controlled synthetic perturbation experiment.'
    }
  ];

  return (
    <div className="min-h-screen bg-[#FFFFFF]">
      {/* Hero Section */}
      <section className="relative bg-[linear-gradient(270deg,#1C3B41_0%,#1E5B5C_49.42%,#152D31_100%)] overflow-hidden min-h-[797px] flex flex-col">
        
        {/* Navigation Bar */}
        <header className="relative w-full h-[82px] bg-[#1E5B5C] shadow-[5px_0_10px_5px_#1C3B41] z-50 flex items-center shrink-0">
          <div className="w-full max-w-[1536px] mx-auto px-6 md:px-12 lg:px-[95px] flex justify-between items-center h-full">
            
            {/* Logo area */}
            <div className="flex items-center gap-4">
              <img src="/logo.png" alt="FlagRank Logo" className="h-[44px] w-auto object-contain shrink-0" />
              <span className="font-['Alegreya_Sans_SC'] font-normal text-[32px] md:text-[40px] text-[#CCEAEA] leading-[48px]">
                FlagRank
              </span>
            </div>

            {/* Nav links */}
            <nav className="hidden lg:flex items-center gap-[40px] xl:gap-[60px]">
              <Link to="/dashboard" className="font-['Alegreya_Sans_SC'] font-normal text-[20px] text-[#CCEAEA] leading-[24px] hover:text-white transition-colors">Dashboard</Link>
              <Link to="/ranking" className="font-['Alegreya_Sans_SC'] font-normal text-[20px] text-[#CCEAEA] leading-[24px] hover:text-white transition-colors">Ranking Analysis</Link>
              <Link to="/evaluation" className="font-['Alegreya_Sans_SC'] font-normal text-[20px] text-[#CCEAEA] leading-[24px] hover:text-white transition-colors">Research Evaluation</Link>
              <Link to="/#methodology" className="font-['Alegreya_Sans_SC'] font-normal text-[20px] text-[#CCEAEA] leading-[24px] hover:text-white transition-colors">Methodology</Link>
            </nav>
            
          </div>
        </header>

        {/* Hero Content */}
        <div className="flex-1 w-full max-w-[1536px] mx-auto px-6 md:px-12 lg:px-[107px] pt-[80px] pb-16 flex flex-col lg:flex-row items-start justify-between gap-12 z-10">
          
          <div className="flex flex-col max-w-[596px] pt-[40px]">
            <h1 className="font-sans font-normal text-[40px] md:text-[48px] leading-[1.15] text-[#B4D5DC] mb-[20px] md:mb-[40px]" style={{ fontFamily: '"Alan Sans", sans-serif' }}>
              A Data-Driven Framework for Detecting Ranking Anomalies
            </h1>
            
            <p className="font-['Alef'] font-normal text-[18px] md:text-[20px] leading-[1.5] text-[#EEFFFF] mb-[40px]">
              Evaluate search-ranking behaviour through observable product attributes, expected-rank estimation, and query-level comparison.
            </p>
            
            <Link 
              to="/dashboard" 
              className="flex items-center justify-center w-[183px] h-[47px] bg-[#E6F7FA] rounded-[30px] font-['Inter'] font-normal text-[20px] text-[#1C3B41] leading-[24px] hover:bg-white transition-colors"
            >
              Try it
            </Link>
          </div>

          {/* Hero Image */}
          <div className="w-full lg:w-[707px] h-[300px] md:h-[437px] bg-black/20 rounded-[40px] shrink-0 lg:mt-[20px] overflow-hidden flex items-center justify-center">
            <img src="/Hero-1.png" alt="FlagRank Dashboard Preview" className="w-full h-full object-cover" />
          </div>

        </div>
      </section>

      {/* Methodology Section */}
      <section id="methodology" className="w-full max-w-[1536px] mx-auto px-6 md:px-12 lg:px-[119px] py-16 md:py-[78px] scroll-mt-[82px]">
        
        <h2 className="font-['Alegreya_Sans_SC'] font-medium text-[32px] md:text-[40px] leading-[48px] text-[#1C3B41] mb-[18px]">
          Research Methodology
        </h2>
        
        <p className="font-['Alef'] font-normal text-[18px] md:text-[20px] leading-[1.5] text-[#1E5B5C] mb-[58px]">
          The end-to-end analytical pipeline for identifying relative ranking inconsistency.
        </p>

        <h3 className="font-['Alef'] font-bold text-[26px] md:text-[32px] leading-[1.5] text-[#1E5B5C] mb-[32px]">
          Pipeline Architecture
        </h3>

        <div className="relative pl-[40px] md:pl-[111px]">
          
          {/* Main timeline vertical line */}
          <div className="absolute left-[39px] md:left-[39px] top-[40px] bottom-[40px] w-0 border-l-2 border-[#B4D5DC] z-0"></div>

          <div className="flex flex-col gap-[37px] relative z-10 pb-[60px]">
            {steps.map((step) => (
              <div key={step.id} className="relative w-full max-w-[1141px]">
                
                {/* Circle Icon */}
                <div className="absolute left-[-40px] md:left-[-111px] top-1/2 -translate-y-1/2 w-[80px] h-[80px] bg-[#EEFFFF] rounded-[50px] shadow-[0px_4px_4px_#1C3B41] flex items-center justify-center z-20">
                  <step.icon className="w-[40px] h-[40px] md:w-[48px] md:h-[48px] text-[#1C3B41]" strokeWidth={1.5} />
                </div>

                {/* Card */}
                <div className="w-full min-h-[177px] bg-[#EEFFFF] rounded-[20px] drop-shadow-[0px_4px_4px_#1C3B41] flex flex-col justify-center p-[20px] md:px-[39px] md:py-[31px]">
                  <h4 className="font-['Alef'] font-bold text-[20px] leading-[1.5] text-[#1C3B41] mb-[20px]">
                    {step.title}
                  </h4>
                  <div className="font-['Alef'] font-normal text-[18px] md:text-[20px] leading-[1.5] text-[#1C3B41]">
                    {step.description}
                  </div>
                </div>

              </div>
            ))}
          </div>

        </div>

        {/* Research Boundary Box */}
        <div className="w-full max-w-[1252px] bg-[#E6F7FA] border border-[#B4D5DC] rounded-[10px] p-[30px] md:p-[45px] lg:px-[90px] lg:py-[70px] mt-12 flex flex-col justify-start">
          
          <div className="flex items-center gap-4 mb-6">
             <div className="w-[40px] h-[40px] flex items-center justify-center bg-[#E6F7FA] text-[#1C3B41] border-[3px] border-[#1C3B41] rounded-full shrink-0">
                <span className="font-bold font-['Alef'] text-xl">i</span>
             </div>
             <h3 className="font-['Alef'] font-bold text-[26px] md:text-[32px] leading-[1.5] text-[#1E5B5C]">
               Research Boundary
             </h3>
          </div>

          <ul className="font-['Alef'] font-normal text-[18px] md:text-[20px] leading-[1.5] text-[#1E5B5C] list-disc pl-8 space-y-2">
            <li>The framework uses publicly observable ranking and product signals.</li>
            <li>It does not reverse-engineer proprietary marketplace ranking algorithms.</li>
            <li>It does not claim to prove intentional manipulation.</li>
            <li>It does not establish causality.</li>
            <li>It does not provide manipulation probability.</li>
            <li>The Suspiciousness Score is not a probability or confidence value.</li>
            <li>The synthetic evaluation is controlled experimental evidence, not real-world validation.</li>
            <li>The current evaluation has no independently verified real-world manipulation labels.</li>
          </ul>

        </div>

      </section>
    </div>
  );
}
