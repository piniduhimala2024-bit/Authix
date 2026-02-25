import { withAuth } from 'next-auth/middleware';

export default withAuth({
  callbacks: {
    authorized: ({ req, token }) => {
      const path = req.nextUrl.pathname;
      if (path.startsWith('/admin')) return token?.role === 'ADMIN';
      return !!token;
    }
  }
});

export const config = {
  matcher: ['/dashboard/:path*', '/admin/:path*']
};
