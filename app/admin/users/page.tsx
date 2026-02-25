import { prisma } from '@/lib/db/prisma';

export default async function AdminUsersPage() {
  const users = await prisma.user.findMany({ take: 50, orderBy: { createdAt: 'desc' } });
  return <div className="card"><h1 className="text-2xl font-bold">Manage Users</h1><ul className="mt-3 space-y-2">{users.map((u) => <li key={u.id}>{u.email} — {u.role} — {u.banned ? 'Banned' : 'Active'}</li>)}</ul></div>;
}
