'use client';

import { useEffect, useState } from 'react';

type Ticket = { id: string; subject: string; status: string };

export default function TicketsPage() {
  const [tickets, setTickets] = useState<Ticket[]>([]);
  useEffect(() => { fetch('/api/user/tickets').then((r) => r.json()).then(setTickets); }, []);
  return <div className="card"><h1 className="text-2xl font-bold">Support Tickets</h1><ul className="mt-3 space-y-2">{tickets.map((t) => <li key={t.id}>{t.subject} — {t.status}</li>)}</ul></div>;
}
