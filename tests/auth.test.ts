import { describe, it, expect } from 'vitest';
import { hashPassword, verifyPassword } from '../lib/security/password';

describe('auth password hashing', () => {
  it('hashes and verifies passwords', async () => {
    const plain = 'ChangeMe123!';
    const hash = await hashPassword(plain);
    expect(hash).not.toEqual(plain);
    expect(await verifyPassword(plain, hash)).toBe(true);
  });
});
