import type { AppState, DailyTask, DailyTip, MouseTip, Player, ScoreEvent, Team, UserMessage } from '../types'

export const teams: Team[] = [
  {
    id: 'joukkue-1',
    name: 'Joukkue 1',
    accent: '#f7e87a'
  },
  {
    id: 'joukkue-2',
    name: 'Joukkue 2',
    accent: '#8bd3f7'
  }
]

export const players: Player[] = [
  {
    id: 'jesse',
    name: 'Jesse',
    teamId: 'joukkue-1'
  },
  {
    id: 'jenni',
    name: 'Jenni',
    teamId: 'joukkue-2'
  }
]

export const rules = [
  'Joukkueet keräävät pisteitä päivän tehtävistä, hiiritehtävistä ja bonuksista.',
  'Päivätehtävän pisteet vahvistetaan, kun suoritus on palautettu.',
  'Hiiri merkitään löydetyksi vasta, kun koko joukkue hyväksyy löydön.',
  'Tasatilanteessa ratkaisee päivän paras perustelu.'
]

const initialScoreEvents: ScoreEvent[] = [
  {
    id: 'seed-1',
    teamId: 'joukkue-1',
    category: 'paivatehtava',
    dailyTaskId: 'day-1',
    title: 'Päivätehtävä',
    points: 10,
    description: 'Kananmunatehtävä palautettu. Pisteen vähennykset: yksi muna rikkoutui.',
    createdAt: '2026-06-30T14:07:00.000Z'
  },
  {
    id: 'seed-2',
    teamId: 'joukkue-1',
    category: 'hiiritehtava',
    title: 'Hiiritehtävä',
    points: 16,
    description: 'Ensimmäinen hiiri löydetty.',
    createdAt: '2026-06-30T14:18:00.000Z'
  },
  {
    id: 'seed-3',
    teamId: 'joukkue-2',
    category: 'paivatehtava',
    dailyTaskId: 'day-1',
    title: 'Päivätehtävä',
    points: 10,
    description: 'Päivätehtävä palautettu.',
    createdAt: '2026-06-30T14:12:00.000Z'
  }
]

const initialMouseTips: MouseTip[] = [
  {
    id: 'tip-1',
    mouseId: 'white',
    text: 'Ensimmäinen vinkki ilmestyy, jos valkoinen hiiri pysyy piilossa iltapäivään asti.',
    createdAt: '2026-06-30T10:00:00.000Z'
  }
]

const initialDailyTips: DailyTip[] = [
  {
    id: 'daily-tip-1',
    dailyTaskId: 'day-1',
    text: 'Host voi lisätä päivän aikana lisävinkkejä, jos tehtävä kaipaa tarkennusta.',
    createdAt: '2026-06-30T10:05:00.000Z'
  }
]

const initialUserMessages: UserMessage[] = []

function createInitialDailyTask (): DailyTask {
  const startsAt = new Date(Date.now() + 7 * 60 * 1000)
  const endsAt = new Date(startsAt.getTime() + 57 * 60 * 1000)

  return {
    id: 'day-1',
    title: 'Päivätehtävä',
    location: 'olohuoneessa',
    startsAt: startsAt.toISOString(),
    endsAt: endsAt.toISOString(),
    preparationText: 'Olkaa koko joukkue paikalla, kun lähtölaskenta päättyy. Ohjeet avataan järjestäjän merkistä.',
    instructions: 'Rakentakaa joukkueellenne kesäinen tunnus. Lopputuloksessa pitää näkyä joukkueen nimi, värit ja vähintään yksi salainen yksityiskohta. Kun aika loppuu, työ pysähtyy ja host kirjaa pisteet.',
    guidanceVisible: false
  }
}

export function createInitialState (): AppState {
  const dailyTask = createInitialDailyTask()

  return {
    teams,
    players,
    dailyTask,
    dailyTasks: [dailyTask],
    activeDailyTaskId: dailyTask.id,
    scoreEvents: initialScoreEvents,
    foundMice: [],
    mouseTips: initialMouseTips,
    mouseTipsSeenAt: null,
    dailyTips: initialDailyTips,
    userMessages: initialUserMessages,
    userMessagesSeenAt: null,
    userMessagesSeenAtByPlayerId: {}
  }
}
