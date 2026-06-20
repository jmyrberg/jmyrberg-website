export type TeamId = string
export type ScoreCategory = 'paivatehtava' | 'hiiritehtava' | 'bonus'
export type MouseId = 'white' | 'pink' | 'black'
export type TaskStatus = 'upcoming' | 'live' | 'ended'

export interface Team {
  id: TeamId
  name: string
  accent: string
}

export interface Player {
  id: string
  name: string
  teamId: TeamId | null
  inviteCode?: string
}

export interface ScoreEvent {
  id: string
  teamId: TeamId
  category: ScoreCategory
  dailyTaskId?: string
  title: string
  points: number
  description: string
  createdAt: string
}

export interface FoundMouse {
  mouseId: MouseId
  teamId: TeamId
  foundAt: string
}

export interface MouseTip {
  id: string
  mouseId: MouseId
  text: string
  createdAt: string
}

export interface DailyTip {
  id: string
  dailyTaskId: string
  text: string
  createdAt: string
}

export interface UserMessage {
  id: string
  recipientPlayerId: string
  text: string
  createdAt: string
}

export interface DailyTask {
  id: string
  title: string
  location: string
  announcementStartsAt: string
  startsAt: string
  endsAt: string
  preparationText: string
  instructions: string
  guidanceVisible: boolean
}

export interface AppState {
  teams: Team[]
  players: Player[]
  dailyTask: DailyTask
  dailyTasks: DailyTask[]
  activeDailyTaskId: string
  scoreEvents: ScoreEvent[]
  foundMice: FoundMouse[]
  mouseTips: MouseTip[]
  mouseTipsSeenAt: string | null
  dailyTips: DailyTip[]
  userMessages: UserMessage[]
  userMessagesSeenAt: string | null
  userMessagesSeenAtByPlayerId: Record<string, string>
}

export interface MouseAsset {
  id: MouseId
  label: string
  image: string
  foundImage: string
}
