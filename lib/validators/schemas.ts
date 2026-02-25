import { z } from 'zod';

export const credentialsSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
});

export const productSchema = z.object({
  type: z.enum(['VPN', 'VPS', 'HOSTING', 'OTHER']),
  name: z.string().min(2),
  description: z.string().min(10),
  priceMonthly: z.coerce.number().positive(),
  priceYearly: z.coerce.number().positive(),
  features: z.array(z.string().min(2)),
  featured: z.boolean().optional(),
  active: z.boolean().optional()
});

export const contactSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  message: z.string().min(10)
});
