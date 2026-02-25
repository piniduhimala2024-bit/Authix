'use client';

import { useState } from 'react';

export default function RegisterPage() {
  const [ok, setOk] = useState(false);
  const [error, setError] = useState('');

  return (
    <div className="card mx-auto max-w-md">
      <h1 className="text-2xl font-bold">Create account</h1>
      {ok ? <p className="mt-3 text-emerald-300">Account created. Please login.</p> : (
        <form className="mt-4 space-y-3" onSubmit={async (e) => {
          e.preventDefault();
          setError('');
          const payload = Object.fromEntries(new FormData(e.currentTarget).entries());
          const res = await fetch('/api/user/profile', { method: 'POST', body: JSON.stringify(payload) });
          if (!res.ok) setError('Unable to create account'); else setOk(true);
        }}>
          <input className="input" name="name" placeholder="Name" required />
          <input className="input" name="email" type="email" placeholder="Email" required />
          <input className="input" name="password" type="password" placeholder="Password" required />
          {error && <p className="text-red-300">{error}</p>}
          <button className="btn-primary w-full">Register</button>
        </form>
      )}
    </div>
  );
}
