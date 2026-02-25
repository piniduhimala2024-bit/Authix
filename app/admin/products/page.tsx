import { prisma } from '@/lib/db/prisma';

export default async function AdminProductsPage() {
  const products = await prisma.product.findMany();
  return <div className="card"><h1 className="text-2xl font-bold">Manage Products</h1><ul className="mt-3 space-y-2">{products.map((p) => <li key={p.id}>{p.name} ({p.type}) — {p.active ? 'Active' : 'Inactive'}</li>)}</ul></div>;
}
