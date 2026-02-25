import { describe, it, expect } from 'vitest';
import { productSchema } from '../lib/validators/schemas';

describe('product schema validation', () => {
  it('accepts valid payload', () => {
    const result = productSchema.safeParse({
      type: 'VPN',
      name: 'Plan',
      description: 'Secure VPN plan for teams',
      priceMonthly: 100,
      priceYearly: 1000,
      features: ['A', 'B']
    });
    expect(result.success).toBe(true);
  });
});
