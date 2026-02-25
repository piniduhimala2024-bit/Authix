import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { prisma } from '@/lib/db/prisma';
import { stripe } from '@/lib/payments/stripe';

export async function GET(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) return NextResponse.redirect(new URL('/login', req.url));

  const productId = req.nextUrl.searchParams.get('productId');
  if (!productId) return NextResponse.json({ error: 'Missing product' }, { status: 400 });
  const product = await prisma.product.findUnique({ where: { id: productId } });
  if (!product) return NextResponse.json({ error: 'Not found' }, { status: 404 });

  const order = await prisma.order.create({ data: { userId: session.user.id, total: product.priceMonthly, currency: 'LKR' } });

  const checkout = await stripe.checkout.sessions.create({
    mode: 'payment',
    line_items: [{ quantity: 1, price_data: { currency: 'lkr', unit_amount: Number(product.priceMonthly) * 100, product_data: { name: product.name } } }],
    success_url: `${process.env.NEXT_PUBLIC_APP_URL}/dashboard/orders`,
    cancel_url: `${process.env.NEXT_PUBLIC_APP_URL}/store`,
    metadata: { orderId: order.id, userId: session.user.id, productId: product.id }
  });

  await prisma.order.update({ where: { id: order.id }, data: { stripeSessionId: checkout.id } });
  return NextResponse.redirect(checkout.url ?? `${process.env.NEXT_PUBLIC_APP_URL}/store`);
}
