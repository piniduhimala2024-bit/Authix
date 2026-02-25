'use client';

import { signIn } from 'next-auth/react';
import { useState } from 'react';

export default function LoginPage() {
  const [error, setError] = useState('');
  return (
    <div className="card mx-auto max-w-md">
      <h1 className="text-2xl font-bold">Login</h1>
      <form className="mt-4 space-y-3" onSubmit={async (e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const result = await signIn('credentials', {
          email: formData.get('email'),
          password: formData.get('password'),
          redirect: true,
          callbackUrl: '/dashboard'
        });
        if (result?.error) setError('Invalid credentials');
      }}>
        <input name="email" type="email" className="input" placeholder="Email" />
        <input name="password" type="password" className="input" placeholder="Password" />
        {error && <p className="text-red-300">{error}</p>}
        <button className="btn-primary w-full">Sign in</button>
      </form>
    </div>
  );
}
