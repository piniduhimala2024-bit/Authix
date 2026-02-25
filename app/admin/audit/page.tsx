import { prisma } from '@/lib/db/prisma';

export default async function AdminAuditPage() {
  const logs = await prisma.auditLog.findMany({ orderBy: { createdAt: 'desc' }, take: 100 });
  return <div className="card"><h1 className="text-2xl font-bold">Audit Logs</h1><ul className="mt-3 space-y-2">{logs.map((l) => <li key={l.id}>{l.action} on {l.entity} by {l.adminId}</li>)}</ul></div>;
}
