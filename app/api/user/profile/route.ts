import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { credentialsSchema } from '@/lib/validators/schemas';
import { hashPassword } from '@/lib/security/password';

export async function POST(req: NextRequest) {
  const body = await req.json();
  const parsed = credentialsSchema.extend({ name: credentialsSchema.shape.email.transform(() => '') }).safeParse(body);
  if (!body.name || !parsed.success) return NextResponse.json({ error: 'Invalid data' }, { status: 400 });
  const existing = await prisma.user.findUnique({ where: { email: body.email } });
  if (existing) return NextResponse.json({ error: 'Email in use' }, { status: 409 });
  const user = await prisma.user.create({
    data: { name: body.name, email: body.email, passwordHash: await hashPassword(body.password) }
  });
  return NextResponse.json({ id: user.id }, { status: 201 });
}
