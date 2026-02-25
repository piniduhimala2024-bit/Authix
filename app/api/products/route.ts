import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/db/prisma';
import { productSchema } from '@/lib/validators/schemas';
import { auth } from '@/lib/auth';

export async function GET() {
  const products = await prisma.product.findMany({ where: { active: true } });
  return NextResponse.json(products);
}

export async function POST(req: NextRequest) {
  const session = await auth();
  if (session?.user?.role !== 'ADMIN') return NextResponse.json({ error: 'Forbidden' }, { status: 403 });

  const parsed = productSchema.safeParse(await req.json());
  if (!parsed.success) return NextResponse.json(parsed.error.format(), { status: 400 });

  const product = await prisma.product.create({
    data: {
      ...parsed.data,
      priceMonthly: parsed.data.priceMonthly,
      priceYearly: parsed.data.priceYearly
    }
  });

  return NextResponse.json(product, { status: 201 });
}
