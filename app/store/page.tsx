import Link from 'next/link';
import { prisma } from '@/lib/db/prisma';

export default async function StorePage({ searchParams }: { searchParams: { q?: string; type?: string } }) {
  const where = {
    active: true,
    ...(searchParams.type ? { type: searchParams.type as any } : {}),
    ...(searchParams.q
      ? { OR: [{ name: { contains: searchParams.q, mode: 'insensitive' as const } }, { description: { contains: searchParams.q, mode: 'insensitive' as const } }] }
      : {})
  };
  const products = await prisma.product.findMany({ where });

  return (
    <div className="space-y-4">
      <h1 className="text-3xl font-bold">Store</h1>
      <form className="card grid gap-3 md:grid-cols-3">
        <input name="q" placeholder="Search plans" className="input" defaultValue={searchParams.q} />
        <select name="type" className="input" defaultValue={searchParams.type}><option value="">All</option><option>VPN</option><option>VPS</option><option>HOSTING</option></select>
        <button className="btn-primary" type="submit">Filter</button>
      </form>
      <div className="grid gap-4 md:grid-cols-2">
        {products.map((product) => (
          <div key={product.id} className="card">
            <h2 className="font-semibold">{product.name}</h2>
            <p className="text-sm text-white/70">{product.description}</p>
            <div className="mt-4 flex justify-between"><span>LKR {product.priceMonthly.toString()}</span><Link className="btn-primary" href={`/api/stripe/checkout?productId=${product.id}`}>Checkout</Link></div>
          </div>
        ))}
      </div>
    </div>
  );
}
