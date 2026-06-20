import { NavLink } from 'react-router-dom';
import { Hop as Home, Truck, CalendarDays, MapPin, ChartBar as BarChart3, FileText, DollarSign, ShieldCheck, Flag, Wrench, Users, Route } from 'lucide-react';

const navItems = [
  { label: 'Dashboard', to: '/dashboard', icon: Home },
  { label: 'Vehicles', to: '/vehicles', icon: Truck },
  { label: 'Bookings', to: '/bookings', icon: CalendarDays },
  { label: 'Customers', to: '/customers', icon: Users },
  { label: 'Trips', to: '/trips', icon: Route },
  { label: 'Calendar', to: '/calendar', icon: MapPin },
  { label: 'Dispatch', to: '/dispatch', icon: Flag },
  { label: 'Maintenance', to: '/maintenance', icon: Wrench },
  { label: 'Expenses', to: '/expenses', icon: FileText },
  { label: 'Profit', to: '/profit', icon: DollarSign },
  { label: 'Invoices', to: '/invoices', icon: BarChart3 },
  { label: 'Renewals', to: '/renewals', icon: ShieldCheck },
];

export function Sidebar() {
  return (
    <aside className="hidden lg:flex lg:w-72 lg:flex-col lg:border-r lg:border-slate-200 lg:bg-white lg:py-8 lg:px-6">
      <div className="mb-10">
        <div className="text-2xl font-semibold text-slate-900">VahanOne</div>
        <p className="mt-2 text-sm text-slate-500">Fleet finance and operations</p>
      </div>

      <nav className="space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                  isActive ? 'bg-slate-100 text-slate-900' : 'text-slate-600 hover:bg-slate-50'
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
    </aside>
  );
}
