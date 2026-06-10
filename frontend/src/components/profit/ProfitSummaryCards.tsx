import { ArrowUpRight, DollarSign, FileText } from 'lucide-react';
import { Card } from '../../components/ui/Card';
import type { ProfitSummary } from '../../types';

interface ProfitSummaryCardsProps {
  summary: ProfitSummary | null;
  loading: boolean;
}

function formatCurrency(value: number) {
  return `₹${value.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 })}`;
}

export function ProfitSummaryCards({ summary, loading }: ProfitSummaryCardsProps) {
  const cards = [
    {
      title: 'Total Revenue',
      value: summary ? formatCurrency(summary.totalRevenue) : '—',
      icon: DollarSign,
      accent: 'bg-slate-100 text-slate-700',
    },
    {
      title: 'Total Expenses',
      value: summary ? formatCurrency(summary.totalExpense) : '—',
      icon: FileText,
      accent: 'bg-amber-100 text-amber-700',
    },
    {
      title: 'Total Profit',
      value: summary ? formatCurrency(summary.totalProfit) : '—',
      icon: ArrowUpRight,
      accent: 'bg-emerald-100 text-emerald-700',
    },
  ];

  return (
    <div className="grid gap-4 lg:grid-cols-3">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <Card key={card.title} className="rounded-3xl border border-slate-200 p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm font-medium uppercase tracking-[0.16em] text-slate-500">{card.title}</p>
                <p className="mt-4 text-3xl font-semibold text-slate-900">{loading ? 'Loading…' : card.value}</p>
              </div>
              <div className={`flex h-12 w-12 items-center justify-center rounded-3xl ${card.accent}`}>
                <Icon className="h-5 w-5" />
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}
