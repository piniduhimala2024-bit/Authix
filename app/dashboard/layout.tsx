import Link from 'next/link';

const links = [
  ['/dashboard', 'Overview'],
  ['/dashboard/orders', 'My Orders'],
  ['/dashboard/subscriptions', 'Subscriptions'],
  ['/dashboard/services/vpn', 'VPN'],
  ['/dashboard/services/vps', 'VPS'],
  ['/dashboard/services/hosting', 'Hosting'],
  ['/dashboard/tickets', 'Tickets'],
  ['/dashboard/wallet', 'Wallet'],
  ['/dashboard/profile', 'Profile'],
  ['/dashboard/notifications', 'Notifications']
];

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid gap-6 md:grid-cols-[220px_1fr]">
      <aside className="card h-fit space-y-2">
        {links.map(([href, label]) => <Link key={href} href={href} className="block rounded px-2 py-1 hover:bg-white/10">{label}</Link>)}
      </aside>
      <div>{children}</div>
    </div>
  );
}
