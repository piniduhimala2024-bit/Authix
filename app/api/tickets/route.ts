import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';

export async function GET() {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json([], { status: 401 });
  const tickets = await prisma.ticket.findMany({ where: { userId: session.user.id }, include: { messages: true } });
  return NextResponse.json(tickets);
}

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  const { subject, message } = await req.json();
  const ticket = await prisma.ticket.create({
    data: {
      userId: session.user.id,
      subject,
      messages: { create: { message, senderUserId: session.user.id } }
    }
  });
  return NextResponse.json(ticket, { status: 201 });
}
