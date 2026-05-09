import React from 'react';
import { GraduationCap, Loader2 } from 'lucide-react';
import { Message } from '../types';

interface MessageBubbleProps {
  message: Message;
  onTraceClick: (checkpoint: number) => void;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, onTraceClick }) => {
  const isUser = message.role === "user";
  const formatTime = (date: Date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  if (message.isLoading) {
    return (
      <div className="flex justify-start mb-6 animate-fade-slide-up">
        <div className="max-w-[75%]">
          <div className="flex items-center gap-1.5 mb-1.5 pl-1">
            <GraduationCap size={12} className="text-amber-400" />
            <span className="text-xs text-amber-400/80 font-semibold tracking-wide">XYZ Advisor</span>
          </div>
          <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 border-l-2 border-l-blue-600 flex items-center gap-3">
             <div className="flex gap-1">
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-typing-bounce" style={{ animationDelay: '0ms' }}></div>
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-typing-bounce" style={{ animationDelay: '150ms' }}></div>
              <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-typing-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
            <span className="text-xs text-slate-500 font-mono italic">Analyzing...</span>
          </div>
        </div>
      </div>
    );
  }

  if (isUser) {
    return (
      <div className="flex justify-end mb-4 animate-fade-slide-up">
        <div className="max-w-[70%] bg-blue-900/40 border border-blue-800/50 rounded-2xl rounded-tr-sm px-4 py-3">
          <p className="text-sm text-slate-200 leading-relaxed font-body">
            {message.content}
          </p>
          <p className="text-xs text-slate-600 mt-1.5 text-right font-mono">
            {formatTime(message.timestamp)}
          </p>
        </div>
      </div>
    );
  }

  const trace = message.trace;

  return (
    <div className="flex justify-start mb-6 animate-fade-slide-up">
      <div className="max-w-[75%]">
        {/* Advisor label */}
        <div className="flex items-center gap-1.5 mb-1.5 pl-1">
          <GraduationCap size={12} className="text-amber-400" />
          <span className="text-xs text-amber-400/80 font-semibold tracking-wide">
            XYZ Advisor
          </span>
          <span className="text-xs text-slate-700 font-mono ml-4">
            {formatTime(message.timestamp)}
          </span>
        </div>
        
        {/* Message content */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl rounded-tl-sm px-4 py-3 border-l-2 border-l-blue-600 shadow-sm">
          <p className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap font-body">
            {message.content}
          </p>
        </div>
        
        {/* Minimal checkpoint row */}
        {trace && (
          <div className="flex items-center gap-2 mt-2 pl-1">
            {/* Checkpoint 1 - Retrieval */}
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full ${
                trace?.find(t => t.checkpoint === 1)?.status === 'pass' 
                  ? 'bg-emerald-500' : 'bg-slate-600'
              }`} />
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tight">
                {trace?.find(t => t.checkpoint === 1)?.status === 'skip' 
                  ? 'direct' : 'retrieved'}
              </span>
            </div>
            
            <span className="text-slate-800 text-[10px]">•</span>
            
            {/* Checkpoint 2 - Grading */}
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full ${
                trace?.find(t => t.checkpoint === 2)?.web_search_triggered 
                  ? 'bg-amber-500' 
                  : trace?.find(t => t.checkpoint === 2)?.status === 'pass'
                    ? 'bg-emerald-500' : 'bg-slate-600'
              }`} />
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tight">
                {trace?.find(t => t.checkpoint === 2)?.web_search_triggered 
                  ? 'web' 
                  : `${trace?.find(t => t.checkpoint === 2)?.docs_relevant ?? 0}/${trace?.find(t => t.checkpoint === 2)?.docs_graded ?? 0} docs`}
              </span>
            </div>
            
            <span className="text-slate-800 text-[10px]">•</span>
            
            {/* Checkpoint 3 - Hallucination */}
            <div className="flex items-center gap-1.5">
              <div className={`w-2 h-2 rounded-full ${
                (trace?.find(t => t.checkpoint === 3)?.retries_used ?? 0) > 0 
                  ? 'bg-amber-500' : 'bg-emerald-500'
              }`} />
              <span className="text-[10px] font-mono text-slate-500 uppercase tracking-tight">verified</span>
            </div>
            
            {/* Expand trace button */}
            <button 
              onClick={() => onTraceClick(0)} // Pass 0 or any dummy, trace panel handles active message
              className="ml-auto text-[10px] text-slate-600 hover:text-blue-400 font-mono transition-colors uppercase tracking-wider"
            >
              view trace ›
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
