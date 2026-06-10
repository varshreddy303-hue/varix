import { cn } from '../../lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ className, ...props }: CardProps) {
  return <div className={cn('rounded-3xl border border-slate-200 bg-white p-6 shadow-sm shadow-slate-200/50', className)} {...props} />;
}
