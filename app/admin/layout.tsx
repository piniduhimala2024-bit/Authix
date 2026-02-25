import Link from 'next/link';

const links = [
  ['/admin', 'Analytics'],
  ['/admin/users', 'Users'],
  ['/admin/products', 'Products'],
  ['/admin/orders', 'Orders'],
  ['/admin/tickets', 'Tickets'],
  ['/admin/settings', 'Settings'],
  ['/admin/audit', 'Audit Logs']
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid gap-6 md:grid-cols-[220px_1fr]">
      <aside className="card h-fit space-y-2">{links.map(([href, label]) => <Link key={href} href={href} className="block rounded px-2 py-1 hover:bg-white/10">{label}</Link>)}</aside>
      <div>{children}</div>
    </div>
  );
}
