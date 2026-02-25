import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="space-y-12">
      <section className="card text-center">
        <p className="mb-3 text-brand-gold">Trusted in Sri Lanka, built for global teams</p>
        <h1 className="text-4xl font-bold">Secure VPN, VPS, Hosting & Managed Digital Services</h1>
        <p className="mx-auto mt-4 max-w-2xl text-white/75">Ceylon Secure Network delivers privacy-first infrastructure with transparent pricing, local support, and global reliability.</p>
        <div className="mt-6 flex justify-center gap-3">
          <Link href="/store" className="btn-primary">Explore Plans</Link>
          <Link href="/contact" className="rounded-lg border border-white/20 px-4 py-2">Talk to Sales</Link>
        </div>
      </section>
      <section className="grid gap-4 md:grid-cols-3">
        {['Business VPN', 'Scalable VPS', 'Managed Hosting'].map((item) => (
          <article key={item} className="card"><h3 className="text-lg font-semibold">{item}</h3><p className="mt-2 text-sm text-white/70">Security-focused delivery with SLA-driven operations and support.</p></article>
        ))}
      </section>
    </div>
  );
}
