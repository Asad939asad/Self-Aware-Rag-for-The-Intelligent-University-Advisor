import React, { useRef, useEffect } from 'react';
import { 
  Terminal, 
  ChevronUp, 
  ChevronDown, 
  CheckCircle2, 
  XCircle, 
  FastForward, 
  Loader2, 
  Globe,
  RefreshCcw,
  ArrowRight
} from 'lucide-react';
import { TraceStep } from '../types';

interface TracePanelProps {
  isOpen: boolean;
  onToggle: () => void;
  steps: TraceStep[];
  path: string;
}

const TracePanel: React.FC<TracePanelProps> = ({ isOpen, onToggle, steps, path }) => {
  const panelRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && panelRef.current) {
      panelRef.current.scrollTop = panelRef.current.scrollHeight;
    }
  }, [isOpen, steps]);

  return (
    <div className={`w-full bg-[#050810] border-t border-brand-border transition-all duration-300 flex flex-col ${isOpen ? 'h-52' : 'h-10'}`}>
      {/* Header Toggle */}
      <button 
        onClick={onToggle}
        className="h-10 px-6 flex items-center justify-between hover:bg-brand-border/30 transition-colors shrink-0 group"
      >
        <div className="flex items-center gap-3">
          <Terminal size={14} className="text-brand-muted group-hover:text-brand-accent transition-colors" />
          <span className="text-[11px] font-mono font-bold text-brand-muted group-hover:text-brand-text uppercase tracking-widest">
            Agent Execution Trace
          </span>
          {path && isOpen && (
             <div className="hidden md:flex items-center gap-2 ml-4 px-3 py-0.5 bg-brand-accent/10 rounded-full border border-brand-accent/20">
                <span className="text-[9px] font-mono text-brand-accent/80 font-bold uppercase">Flow Path:</span>
                <span className="text-[9px] font-mono text-brand-muted tracking-tighter overflow-hidden whitespace-nowrap max-w-[400px]">
                  {path}
                </span>
             </div>
          )}
        </div>
        <div className="flex items-center gap-4">
           {steps.length > 0 && !isOpen && (
            <span className="text-[10px] font-mono text-brand-success/60 font-bold uppercase animate-pulse">
              {steps.length} Steps Logged
            </span>
          )}
          {isOpen ? <ChevronDown size={14} className="text-brand-muted" /> : <ChevronUp size={14} className="text-brand-muted" />}
        </div>
      </button>

      {/* Content Area */}
      <div 
        ref={panelRef}
        className={`flex-1 overflow-y-auto px-6 py-4 space-y-4 font-mono text-xs ${isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}
      >
        {steps.length === 0 ? (
          <div className="h-full flex items-center justify-center text-brand-muted/20 flex-col gap-2">
            <Terminal size={24} strokeWidth={1} />
            <span className="text-[10px] uppercase tracking-[0.2em]">Awaiting execution data...</span>
          </div>
        ) : (
          steps.map((step, idx) => {
            const statusConfig = {
              pass: { icon: <CheckCircle2 size={12} className="text-brand-success" />, color: 'text-brand-success' },
              fail: { icon: <XCircle size={12} className="text-brand-danger" />, color: 'text-brand-danger' },
              skip: { icon: <FastForward size={12} className="text-brand-muted" />, color: 'text-brand-muted' },
              pending: { icon: <Loader2 size={12} className="text-brand-muted animate-spin" />, color: 'text-brand-muted' }
            };

            const checkpointConfig = {
              1: { label: 'C1', color: 'bg-brand-accent/20 text-brand-accent border-brand-accent/40' },
              2: { label: 'C2', color: 'bg-brand-warning/20 text-brand-warning border-brand-warning/40' },
              3: { label: 'C3', color: 'bg-brand-checkpoint/20 text-brand-checkpoint border-brand-checkpoint/40' }
            };

            const cp = checkpointConfig[step.checkpoint as 1|2|3];
            const sc = statusConfig[step.status];

            return (
              <div key={idx} className="space-y-1.5 animate-fade-slide-up" style={{ animationDelay: `${idx * 50}ms` }}>
                <div className="flex items-center gap-3">
                  <span className="text-brand-muted/40 tabular-nums">[{new Date(step.timestamp).toLocaleTimeString([], { hour12: false })}]</span>
                  <span className={`text-[9px] px-1.5 py-0.5 rounded border font-black ${cp.color}`}>{cp.label}</span>
                  <div className="shrink-0">{sc.icon}</div>
                  <span className="text-brand-text font-bold uppercase tracking-tight">{step.label}:</span>
                  <span className="text-brand-muted truncate">{step.detail}</span>
                </div>
                
                {step.reasoning && (
                  <div className="pl-24 flex gap-2">
                    <ArrowRight size={10} className="mt-1 text-brand-gold/40 shrink-0" />
                    <p className="text-brand-goldLight/70 italic leading-relaxed text-[11px] font-body">
                      {step.reasoning}
                    </p>
                  </div>
                )}

                {(step.web_search_triggered || step.retries_used! > 0) && (
                  <div className="pl-24 flex gap-2 pt-1">
                    {step.web_search_triggered && (
                      <span className="flex items-center gap-1.5 bg-brand-warning/10 text-brand-warning px-2 py-0.5 rounded border border-brand-warning/20 text-[9px] font-black uppercase">
                        <Globe size={10} />
                        Web Search Fallback
                      </span>
                    )}
                    {step.retries_used! > 0 && (
                      <span className="flex items-center gap-1.5 bg-brand-danger/10 text-brand-danger px-2 py-0.5 rounded border border-brand-danger/20 text-[9px] font-black uppercase">
                        <RefreshCcw size={10} />
                        Retry Count: {step.retries_used}
                      </span>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default TracePanel;
