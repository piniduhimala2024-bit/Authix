import { prisma } from '@/lib/db/prisma';

export default async function AdminTicketsPage() {
  const tickets = await prisma.ticket.findMany({ include: { user: true }, orderBy: { createdAt: 'desc' } });
  return <div className="card"><h1 className="text-2xl font-bold">Manage Tickets</h1><ul className="mt-3 space-y-2">{tickets.map((t) => <li key={t.id}>{t.subject} — {t.status} — {t.user.email}</li>)}</ul></div>;
}
