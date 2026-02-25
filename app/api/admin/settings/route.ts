import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const settings = await prisma.siteSetting.findUnique({ where: { id: 'site' } });
  return NextResponse.json(settings);
}

export async function PATCH(req: NextRequest) {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  const data = await req.json();
  const settings = await prisma.siteSetting.update({ where: { id: 'site' }, data });
  return NextResponse.json(settings);
}
