export const sanitizeInput = (value: string) => value.replace(/[<>]/g, '').trim();
