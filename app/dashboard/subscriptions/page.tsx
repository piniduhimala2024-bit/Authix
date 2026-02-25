import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export default async function SubsPage() {
  const session = await auth();
  const data = await prisma.subscription.findMany({ where: { userId: session?.user?.id }, include: { product: true } });
  return <div className="card"><h1 className="text-2xl font-bold">My Subscriptions</h1><ul className="mt-3 space-y-2">{data.map((s) => <li key={s.id}>{s.product.name} — {s.status} — renew by {new Date(s.currentPeriodEnd).toLocaleDateString()}</li>)}</ul></div>;
}
