import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export default async function DashboardPage() {
  const session = await auth();
  const userId = session?.user?.id ?? '';
  const [orders, subscriptions] = await Promise.all([
    prisma.order.count({ where: { userId } }),
    prisma.subscription.count({ where: { userId, status: 'ACTIVE' } })
  ]);
  return <div className="space-y-4"><h1 className="text-3xl font-bold">Dashboard</h1><div className="grid gap-4 md:grid-cols-2"><div className="card">Orders: {orders}</div><div className="card">Active Services: {subscriptions}</div></div></div>;
}
