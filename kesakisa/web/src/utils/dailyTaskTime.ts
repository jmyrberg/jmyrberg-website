export function defaultTaskAnnouncementStartsAt (startsAt: string): string {
  const startDate = new Date(startsAt)

  if (Number.isNaN(startDate.getTime())) {
    return new Date().toISOString()
  }

  const announcementDate = new Date(startDate)
  announcementDate.setDate(announcementDate.getDate() - 1)
  announcementDate.setHours(18, 0, 0, 0)

  return announcementDate.toISOString()
}

export function hasTaskAnnouncementStarted (announcementStartsAt: string, nowMs = Date.now()): boolean {
  const announcementTime = new Date(announcementStartsAt).getTime()

  return Number.isFinite(announcementTime) && nowMs >= announcementTime
}
