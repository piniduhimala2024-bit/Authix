import { prisma } from '@/lib/db/prisma';

export default async function AdminOrdersPage() {
  const orders = await prisma.order.findMany({ include: { user: true }, orderBy: { createdAt: 'desc' } });
  return <div className="card"><h1 className="text-2xl font-bold">Manage Orders</h1><ul className="mt-3 space-y-2">{orders.map((o) => <li key={o.id}>{o.user.email} — {o.status} — {o.total.toString()}</li>)}</ul></div>;
}
