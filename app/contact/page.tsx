'use client';

import { useState } from 'react';

export default function ContactPage() {
  const [done, setDone] = useState(false);
  const [error, setError] = useState('');

  async function submit(formData: FormData) {
    setError('');
    const res = await fetch('/api/contact', { method: 'POST', body: JSON.stringify(Object.fromEntries(formData.entries())) });
    if (!res.ok) setError('Could not send message');
    else setDone(true);
  }

  return (
    <div className="card max-w-xl">
      <h1 className="text-3xl font-bold">Contact</h1>
      {done ? <p className="mt-4 text-emerald-300">Message sent successfully.</p> : (
        <form action={submit} className="mt-4 space-y-3">
          <input name="name" className="input" placeholder="Name" required />
          <input name="email" type="email" className="input" placeholder="Email" required />
          <textarea name="message" className="input min-h-32" placeholder="How can we help?" required />
          {error && <p className="text-red-300">{error}</p>}
          <button className="btn-primary" type="submit">Send</button>
        </form>
      )}
    </div>
  );
}
