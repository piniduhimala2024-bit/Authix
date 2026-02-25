import { prisma } from '@/lib/db/prisma';

export default async function AdminDashboard() {
  const [users, revenue, orders] = await Promise.all([
    prisma.user.count(),
    prisma.order.aggregate({ _sum: { total: true } }),
    prisma.order.count()
  ]);
  return <div className="grid gap-4 md:grid-cols-3"><div className="card">Users: {users}</div><div className="card">Orders: {orders}</div><div className="card">Revenue: {revenue._sum.total?.toString() ?? 0} LKR</div></div>;
}
