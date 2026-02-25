import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  const [users, orders, revenue] = await Promise.all([prisma.user.count(), prisma.order.count(), prisma.order.aggregate({ _sum: { total: true } })]);
  return NextResponse.json({ users, orders, revenue: revenue._sum.total });
}
