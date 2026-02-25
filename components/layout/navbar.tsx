import Link from 'next/link';

const links = [
  ['Pricing', '/pricing'],
  ['Store', '/store'],
  ['About', '/about'],
  ['Contact', '/contact'],
  ['Status', '/status']
];

export function Navbar() {
  return (
    <header className="border-b border-white/10 bg-brand-navy/80 backdrop-blur">
      <div className="container flex h-16 items-center justify-between">
        <Link href="/" className="font-semibold text-brand-gold">Ceylon Secure Network</Link>
        <nav className="hidden gap-6 text-sm md:flex">
          {links.map(([label, href]) => (
            <Link key={href} href={href as string} className="text-white/80 hover:text-white">{label}</Link>
          ))}
        </nav>
        <div className="flex gap-2">
          <Link href="/login" className="rounded-lg border border-white/20 px-3 py-1.5 text-sm">Login</Link>
          <Link href="/register" className="btn-primary text-sm">Get Started</Link>
        </div>
      </div>
    </header>
  );
}
