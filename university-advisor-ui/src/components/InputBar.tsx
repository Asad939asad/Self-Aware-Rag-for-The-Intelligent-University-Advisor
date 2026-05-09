import React, { useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface InputBarProps {
  value: string;
  onChange: (value: string) => void;
  onSend: () => void;
  isLoading: boolean;
}

const InputBar: React.FC<InputBarProps> = ({ value, onChange, onSend, isLoading }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="p-3 border-t border-slate-800 bg-[#040811] shrink-0">
      <div className="flex gap-2 items-end max-w-4xl mx-auto w-full">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={e => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about courses, faculty, policies..."
          rows={2}
          disabled={isLoading}
          className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200 placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-blue-600 resize-none font-body transition-all disabled:opacity-50"
        />
        <button
          onClick={onSend}
          disabled={isLoading || !value.trim()}
          className="w-12 h-12 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded-xl flex items-center justify-center transition-all shrink-0 shadow-lg shadow-blue-900/10 hover:shadow-blue-900/30 active:scale-95"
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin" />
          ) : (
            <Send size={18} />
          )}
        </button>
      </div>
    </div>
  );
};

export default InputBar;
