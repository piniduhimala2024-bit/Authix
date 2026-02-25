import { PrismaClient, ProductType, Role } from '@prisma/client';
import bcrypt from 'bcryptjs';

const prisma = new PrismaClient();

async function main() {
  const passwordHash = await bcrypt.hash('ChangeMe123!', 12);

  await prisma.user.upsert({
    where: { email: 'admin@ceylonsecurenetwork.lk' },
    update: { role: Role.ADMIN, passwordHash },
    create: {
      email: 'admin@ceylonsecurenetwork.lk',
      name: 'CSN Admin',
      role: Role.ADMIN,
      passwordHash
    }
  });

  const products = [
    {
      type: ProductType.VPN,
      name: 'Ceylon VPN Pro',
      description: 'High privacy VPN with global nodes and business-grade policies.',
      priceMonthly: 2900,
      priceYearly: 29000,
      features: ['AES-256 encryption', 'No-logs policy', 'Multi-device support'],
      featured: true
    },
    {
      type: ProductType.VPS,
      name: 'Lanka VPS Start',
      description: 'Reliable VPS with scalable compute and 99.9% uptime SLA.',
      priceMonthly: 8500,
      priceYearly: 89000,
      features: ['2 vCPU / 4GB RAM', 'NVMe storage', 'Managed firewall']
    },
    {
      type: ProductType.HOSTING,
      name: 'Business Hosting',
      description: 'Secure hosting stack for SMEs and agencies.',
      priceMonthly: 3200,
      priceYearly: 34000,
      features: ['Daily backup', 'Free SSL', 'Performance monitoring']
    }
  ];

  for (const product of products) {
    await prisma.product.upsert({
      where: { id: `${product.type}-${product.name}`.replace(/\s+/g, '-').toLowerCase() },
      update: product,
      create: { id: `${product.type}-${product.name}`.replace(/\s+/g, '-').toLowerCase(), ...product }
    });
  }

  await prisma.siteSetting.upsert({ where: { id: 'site' }, update: {}, create: { id: 'site' } });
}

main().finally(() => prisma.$disconnect());
