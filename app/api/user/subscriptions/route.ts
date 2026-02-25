import { NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json([], { status: 401 });
  return NextResponse.json(await prisma.subscription.findMany({ where: { userId: session.user.id }, include: { product: true } }));
}
