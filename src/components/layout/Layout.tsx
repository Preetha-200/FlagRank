import { Link, Outlet, useLocation } from 'react-router-dom';
import { Search, BarChart2, GitBranch, FlaskConical } from 'lucide-react';

export function Layout() {
  const location = useLocation();

  const navItems = [
    { name: 'Dashboard', path: '/dashboard', icon: BarChart2 },
    { name: 'Ranking Analysis', path: '/ranking', icon: Search },
    { name: 'Research Evaluation', path: '/evaluation', icon: FlaskConical },
    { name: 'Methodology', path: '/#methodology', icon: GitBranch },
  ];

  return (
    <div className="min-h-screen bg-[#E6F7FA] font-['Alef'] text-[#1C3B41]">
      {/* Top Navigation */}
      <header className="sticky top-0 z-50 w-full h-[82px] bg-[#1E5B5C] shadow-[5px_0_10px_5px_#1C3B41]/50 flex items-center shrink-0">
        <div className="w-full max-w-[1536px] mx-auto px-6 md:px-12 lg:px-[119px] flex justify-between items-center h-full">
          
          {/* Logo area */}
          <Link to="/" className="flex items-center gap-4 hover:opacity-90 transition-opacity">
             <div className="flex items-center gap-4">
              <img src="/logo.png" alt="FlagRank Logo" className="h-[44px] w-auto object-contain shrink-0" />
              <span className="font-['Alegreya_Sans_SC'] font-normal text-[32px] md:text-[40px] text-[#CCEAEA] leading-[48px]">
                FlagRank
              </span>
            </div>
          </Link>

          {/* Main Navigation */}
          <nav className="hidden lg:flex items-center gap-[30px] xl:gap-[40px]">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path || (item.path !== '/' && location.pathname.startsWith(item.path));
              return (
                <Link 
                  key={item.name}
                  to={item.path} 
                  className={`font-['Alegreya_Sans_SC'] font-normal text-[20px] leading-[24px] transition-colors flex items-center gap-2
                    ${isActive ? 'text-white border-b-2 border-white pb-1' : 'text-[#CCEAEA] hover:text-white pb-1 border-b-2 border-transparent'}`}
                >
                  {item.name}
                </Link>
              );
            })}
          </nav>
          
          {/* Right side actions */}
          <div className="flex items-center space-x-3 lg:hidden">
             {/* Mobile menu could go here, keeping simple for now */}
          </div>
          
        </div>
      </header>

      {/* Main Content Area */}
      <main className="w-full max-w-[1536px] mx-auto px-6 md:px-12 lg:px-[119px] py-12">
        <Outlet />
      </main>
    </div>
  );
}
