export const LABEL_MAX = 24

export function truncateTitle(title: string, max = LABEL_MAX): string {
  const chars = Array.from(title)
  if (chars.length <= max) return title
  return chars.slice(0, max - 1).join('').trimEnd() + '…'
}
