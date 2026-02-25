import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { contactSchema } from '@/lib/validators/schemas';
import { sanitizeInput } from '@/lib/security/sanitize';
import { sendMail } from '@/lib/email/send';
import { checkRateLimit } from '@/lib/security/rate-limit';

export async function POST(req: NextRequest) {
  const ip = req.headers.get('x-forwarded-for') ?? 'local';
  if (!checkRateLimit(`contact:${ip}`, 10, 60_000)) return NextResponse.json({ error: 'Too many requests' }, { status: 429 });

  const parsed = contactSchema.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json(parsed.error.format(), { status: 400 });

  const data = {
    name: sanitizeInput(parsed.data.name),
    email: parsed.data.email,
    message: sanitizeInput(parsed.data.message)
  };

  await prisma.contactMessage.create({ data });
  await sendMail(data.email, 'We received your message', '<p>Thank you for contacting Ceylon Secure Network.</p>');
  return NextResponse.json({ ok: true });
}
