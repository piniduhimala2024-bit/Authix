import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  return NextResponse.json(await prisma.ticket.findMany({ include: { messages: true, user: true } }));
}

export async function POST(req: NextRequest) {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
  const { ticketId, message, close } = await req.json();
  await prisma.ticketMessage.create({ data: { ticketId, message, senderAdminId: session.user.id } });
  if (close) await prisma.ticket.update({ where: { id: ticketId }, data: { status: 'CLOSED' } });
  return NextResponse.json({ ok: true });
}
