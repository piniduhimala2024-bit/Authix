import type { Metadata } from 'next';
import './globals.css';
import { Navbar } from '@/components/layout/navbar';

export const metadata: Metadata = {
  title: 'Ceylon Secure Network | VPN, VPS, Hosting',
  description: 'Enterprise-grade VPN, VPS, hosting and digital services from Sri Lanka for the world.',
  openGraph: {
    title: 'Ceylon Secure Network',
    description: 'Secure digital infrastructure for modern businesses.',
    images: ['/og-placeholder.png']
  }
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Navbar />
        <main className="container py-10">{children}</main>
      </body>
    </html>
  );
}
