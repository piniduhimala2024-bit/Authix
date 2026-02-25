import { prisma } from '@/lib/db/prisma';

export default async function AdminSettingsPage() {
  const settings = await prisma.siteSetting.findUnique({ where: { id: 'site' } });
  return <div className="card"><h1 className="text-2xl font-bold">Site Settings</h1><p className="mt-3">Company: {settings?.companyName}</p><p>Support: {settings?.supportEmail}</p></div>;
}
