import React from 'react';
import { GraduationCap, Menu } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar: () => void;
}

const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  return (
    <header className="h-14 bg-[#040811] border-b border-slate-800 flex items-center justify-between px-4 shrink-0 z-50">
      <div className="flex items-center gap-3">
        <button 
          onClick={onToggleSidebar} 
          className="text-slate-500 hover:text-slate-300 transition-colors p-1"
        >
          <Menu size={18} />
        </button>
        <div className="flex items-center gap-2">
          <GraduationCap size={18} className="text-amber-400" />
          <span className="text-sm font-semibold text-slate-200"
                style={{fontFamily: 'Playfair Display, serif'}}>
            XYZ National University
          </span>
        </div>
      </div>
      
      <div className="flex items-center gap-2.5 bg-slate-900/50 px-3 py-1.5 rounded-full border border-slate-800">
        <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
        <span className="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-bold">Agent Online</span>
      </div>
    </header>
  );
};

export default Header;
