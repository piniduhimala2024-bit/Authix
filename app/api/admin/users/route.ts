import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  return NextResponse.json(await prisma.user.findMany({ orderBy: { createdAt: 'desc' } }));
}

export async function PATCH(req: NextRequest) {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  const { id, role, banned } = await req.json();
  const user = await prisma.user.update({ where: { id }, data: { role, banned } });
  await prisma.auditLog.create({ data: { adminId: session.user.id, action: 'UPDATE_USER', entity: 'User', entityId: id, metaJson: { role, banned } } });
  return NextResponse.json(user);
}
