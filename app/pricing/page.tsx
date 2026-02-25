import { prisma } from '@/lib/db/prisma';

export default async function PricingPage() {
  const products = await prisma.product.findMany({ where: { active: true } });
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Pricing</h1>
      <div className="grid gap-4 md:grid-cols-3">
        {products.map((product) => (
          <div key={product.id} className="card">
            <h2 className="text-xl font-semibold">{product.name}</h2>
            <p className="text-sm text-white/70">{product.description}</p>
            <p className="mt-4 text-brand-gold">LKR {product.priceMonthly.toString()}/mo</p>
          </div>
        ))}
      </div>
    </div>
  );
}
