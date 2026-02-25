const memory = new Map<string, { count: number; ts: number }>();

export function checkRateLimit(key: string, limit = 30, windowMs = 60_000) {
  const now = Date.now();
  const item = memory.get(key);
  if (!item || now - item.ts > windowMs) {
    memory.set(key, { count: 1, ts: now });
    return true;
  }
  item.count += 1;
  return item.count <= limit;
}
