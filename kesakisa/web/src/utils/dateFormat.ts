function padTimePart (value: number): string {
  return value.toString().padStart(2, '0')
}

export function formatClock (value: string): string {
  const date = new Date(value)

  return `${padTimePart(date.getHours())}:${padTimePart(date.getMinutes())}`
}

export function formatShortDateTime (value: string): string {
  const date = new Date(value)

  return `${date.getDate()}.${date.getMonth() + 1}. ${formatClock(value)}`
}

export function formatWeekdayDateTime (value: string): string {
  const date = new Date(value)
  const weekday = new Intl.DateTimeFormat('fi-FI', { weekday: 'short' }).format(date)

  return `${weekday} ${date.getDate()}.${date.getMonth() + 1}. ${formatClock(value)}`
}

function localDateKey (date: Date): string {
  return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`
}

export function isToday (value: string): boolean {
  return localDateKey(new Date(value)) === localDateKey(new Date())
}

export function isTomorrow (value: string): boolean {
  const tomorrow = new Date()
  tomorrow.setDate(tomorrow.getDate() + 1)

  return localDateKey(new Date(value)) === localDateKey(tomorrow)
}
