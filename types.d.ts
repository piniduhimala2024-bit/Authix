import { Role } from '@prisma/client';

declare module 'next-auth' {
  interface User {
    role?: Role;
  }
  interface Session {
    user: {
      id: string;
      role: Role | string;
      name?: string | null;
      email?: string | null;
    };
  }
}

declare module 'next-auth/jwt' {
  interface JWT {
    role?: Role | string;
  }
}
