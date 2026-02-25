import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function PATCH(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { notificationsOn } = await req.json();
  await prisma.user.update({ where: { id: session.user.id }, data: { notificationsOn: Boolean(notificationsOn) } });
  return NextResponse.json({ ok: true });
}
