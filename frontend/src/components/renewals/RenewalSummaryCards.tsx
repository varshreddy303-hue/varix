import { Calendar, Clock3, ShieldAlert } from 'lucide-react';
import { Card } from '../../components/ui/Card';

interface RenewalSummaryCardsProps {
  loading: boolean;
  expiredCount: number;
  expiringSoonCount: number;
  upcomingEmiCount: number;
}

export function RenewalSummaryCards({ loading, expiredCount, expiringSoonCount, upcomingEmiCount }: RenewalSummaryCardsProps) {
  const cards = [
    {
      title: 'Expired documents',
      value: expiredCount,
      icon: ShieldAlert,
      accent: 'bg-red-100 text-red-700',
    },
    {
      title: 'Expiring within 30 days',
      value: expiringSoonCount,
      icon: Clock3,
      accent: 'bg-amber-100 text-amber-700',
    },
    {
      title: 'Upcoming EMI payments',
      value: upcomingEmiCount,
      icon: Calendar,
      accent: 'bg-sky-100 text-sky-700',
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
