import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export default async function OrdersPage() {
  const session = await auth();
  const orders = await prisma.order.findMany({ where: { userId: session?.user?.id }, orderBy: { createdAt: 'desc' } });
  return <div className="card"><h1 className="text-2xl font-bold">My Orders</h1><ul className="mt-3 space-y-2">{orders.map((o) => <li key={o.id} className="border-b border-white/10 pb-2">{o.id} — {o.status} — {o.total.toString()} {o.currency}</li>)}</ul></div>;
}
