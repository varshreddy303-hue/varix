import { cn } from '../../lib/utils';
import type { ComponentType } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  icon?: ComponentType<{ className?: string }>;
}

export function Input({ className, icon: Icon, ...props }: InputProps) {
  const inputClasses = cn(
    'w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-950 shadow-sm placeholder:text-slate-400 focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200',
    Icon ? 'pl-11' : '',
    className,
  );

  if (!Icon) {
    return <input className={inputClasses} {...props} />;
  }

  return (
    <div className="relative">
      <div className="pointer-events-none absolute inset-y-0 left-4 flex items-center text-slate-400">
        <Icon className="h-4 w-4" />
      </div>
      <input className={inputClasses} {...props} />
    </div>
  );
}
