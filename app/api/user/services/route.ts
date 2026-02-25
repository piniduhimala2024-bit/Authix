import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({ vpn: 'placeholder', vps: 'placeholder', hosting: 'placeholder' });
}
