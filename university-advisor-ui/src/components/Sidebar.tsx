import React from 'react';
import { 
  BookOpen, 
  Users, 
  ShieldCheck, 
  CreditCard, 
  Calendar, 
  GraduationCap
} from 'lucide-react';
import { WindowMemoryItem } from '../types';

interface SidebarProps {
  onQuickTopic: (topic: string) => void;
  windowMemory: WindowMemoryItem[];
  isOpen: boolean;
}

const Sidebar: React.FC<SidebarProps> = ({ onQuickTopic, windowMemory, isOpen }) => {
  if (!isOpen) return null;

  const quickTopics = [
    { label: "Prerequisites", icon: <BookOpen size={14} />, query: "What are the prerequisites for Advanced Algorithms?" },
    { label: "Faculty", icon: <Users size={14} />, query: "Who are the professors in the Computer Science department?" },
    { label: "Policies", icon: <ShieldCheck size={14} />, query: "What is the policy for academic probation?" },
    { label: "Fee Structure", icon: <CreditCard size={14} />, query: "What are the tuition fees for the BSCS program?" },
    { label: "Schedule", icon: <Calendar size={14} />, query: "When does the Fall 2025 semester start?" },
    { label: "Requirements", icon: <GraduationCap size={14} />, query: "What are the total credit hours required for graduation?" },
  ];

  return (
    <aside className="w-64 h-full bg-[#0D1117] border-r border-slate-800 flex flex-col relative shrink-0 transition-all duration-150">
      <div className="p-4">
        {/* Logo area */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <GraduationCap size={18} className="text-amber-400" />
            <span className="text-sm font-semibold text-slate-200" 
                  style={{fontFamily: 'Playfair Display, serif'}}>
              XYZ Advisory
            </span>
          </div>
          <p className="text-xs text-slate-600 pl-6 font-body">
            Self-RAG Course Agent
          </p>
        </div>
        
        {/* Divider */}
        <div className="border-t border-slate-800 mb-4" />
        
        {/* Quick Topics */}
        <p className="text-[10px] text-slate-600 uppercase tracking-[0.2em] mb-3 font-mono">
          Quick Topics
        </p>
        <div className="flex flex-col gap-1">
          {quickTopics.map(topic => (
            <button
              key={topic.label}
              onClick={() => onQuickTopic(topic.query)}
              className="flex items-center gap-3 text-left px-3 py-2 rounded-lg text-xs text-slate-400 
                         hover:bg-slate-800 hover:text-slate-200 
                         transition-colors duration-150 font-body"
            >
              <span className="opacity-50">{topic.icon}</span>
              {topic.label}
            </button>
          ))}
        </div>
        
        {/* Context indicator at bottom */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-slate-900 rounded-lg p-3 border border-slate-800 shadow-sm">
            <p className="text-[10px] font-mono text-slate-600 mb-1 uppercase tracking-wider">
              💬 Memory window
            </p>
            <p className="text-[11px] text-slate-500 font-body">
              {windowMemory.length > 0 
                ? `${windowMemory.length / 2} exchange(s) in context`
                : 'No context yet'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
