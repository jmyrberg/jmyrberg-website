import type { AppState, DailyTask, DailyTip, MouseTip, Player, ScoreEvent, Team, UserMessage } from '../types'
import { defaultTaskAnnouncementStartsAt } from '../utils/dailyTaskTime'

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
  'Maksimipistemäärä kustakin tehtävästä on 10.',
  'Pelaajan jäädessä kiinni huijauksesta tehtävän suoritus hylätään.',
  'Pelaajan sabotoidessa toista pelaajaa tai joukkuetta käynnissä oleva sabotoijan tehtävä hylätään ja 10 pistettä siirretään sabotoijan joukkueelta sabotoidulle. Mikäli pelaaja sabotoi omaa joukkuettaan, hänet poistetaan kisasta 12 tunnin ajaksi.',
  'Pelaajat siivoavat itse tehtävien jäljet tehtävien jälkeen.',
  'Jokaisen pelaajan myöhästymisestä vähennetään 1 piste/minuutti.',
  'Hiirien löydöstä tulee ilmoittaa Jennille mahdollisimman pian. Löydetyt hiiret merkitään Hiiret-välilehdelle.',
  'Koko lisätehtävä tulee lukea kokonaisuudessaan viipymättä heti tehtävän avaamisen jälkeen. Lisätehtävän aika alkaa heti, kun tehtävä on luettu loppuun.',
  'Kännyköiden ja muiden tietoteknisten laitteiden käyttö tehtävien aikana on kielletty, ellei niitä ole erikseen sallittu. Tekoälyn käyttöön vaaditaan erillinen lupa.',
  'Siitä joukkueesta, jossa on 6 pelaajaa, yksi pelaaja siirtyy päivätehtävän ajaksi sivuun, jolloin molemmissa joukkueissa on 5 pelaajaa. Tarvittaessa ylimääräinen pelaaja toimii apulaisena ja auttaa tehtävän järjestämisessä.',
  'Mikäli ylimääräinen pelaaja toimii apulaisena, hän ei saa puhua tai muuten kommunikoida kuulemastaan, näkemästään tai kokemastaan joukkueensa kanssa ennen tehtävää, tehtävän aikana tai sen jälkeen. Mikäli apulainen jää kiinni tai aiheuttaa epäilystä tehtävään liittyvästä kommunikoinnista joukkueensa kanssa, käytetään sabotointisääntöä.',
  'Mikäli kuudes pelaaja ei tuo päivätehtävässä huomattavaa etua joukkueelleen, joukkue voi valita pitää kuudennen pelaajan joukkueessaan, mutta tällöin heiltä vähennetään 1/6 osa tehtävästä saaduista pisteistä.',
  'Päivittäin klo 18.00-18.30 joukkueilla on mahdollisuus pelata Fortunaa ja kerryttää joukkueelleen pisteitä. Fortunan säännöt: joukkueet saavat pelata korkeintaan 10 kuulaa päivässä. Yksi kuula maksaa yhden pisteen. Jokaisen kuulan saa lyödä vain kerran. Kaikki kuulat lyödään vuorotellen ja kerätään lopuksi kaikki kerralla pois. Mikäli kuula valuu takaisin kiitorataan tai laskeutuu pelilaudan alaosaan, se hylätään eikä siitä saa pisteitä. Kuulat, jotka osuvat pistekohtiin, kerryttävät pisteitä.',
  'Salatehtävät ovat henkilökohtaisia, eivät joukkuekohtaisia. Salatehtävät toimitetaan kesäkisasivuston kautta viestitoiminnolla. Jokainen salatehtävä kestää 24 tuntia, ellei pelaaja suorita kertaluontoista tehtävää ennen 24 tunnin loppumista. Pelaajan saadessa salatehtävän hän alkaa suorittaa sitä muiden tietämättä. Jennin ei välttämättä tarvitse olla paikalla tehtävää suorittaessa, kunhan pelaaja pystyy todistamaan suorittaneensa tehtävän. 24 tunnin kuluttua tai seuraavana sopivana hetkenä Jenni kysyy kaikilta pelaajilta, onko kyseinen pelaaja tehnyt salatehtävän. Pisteytys tulee pelaajan panostuksen mukaan. Mikäli pelaajan salatehtävä paljastuu ennen kuin se paljastetaan tai ennen kuin tehtävä on suoritettu, tehtävä hylätään ja pelaaja jää ilman pisteitä.',
  'Viikkotehtävä: molemmille joukkueille on piilotettu viikkotehtävä samaan paikkaan. Joukkue, joka löytää ensimmäisenä viikkotehtävän, ottaa niistä toisen ja jättää toisen paikalleen. Löydettyään viikkotehtävän joukkue alkaa suorittaa sitä valitsemassaan paikassa. Viikkotehtävää saa tehdä korkeintaan 3 pelaajaa kerralla ja korkeintaan 3 tuntia päivässä. Pisteytys tapahtuu joukkueen järjestelmällisyyden, kaikkien joukkueen jäsenten osallisuuden ja suorittamistahdin mukaan. Mikäli molemmat joukkueet suorittavat viikkotehtävän loppuun lauantai-iltaan mennessä, molemmat joukkueet saavat tehtävästä pisteitä. Huom! Viikkotehtävät ovat erilaisissa pakkauksissa, mutta sisällöltään samanlaiset.'
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
    announcementStartsAt: defaultTaskAnnouncementStartsAt(startsAt.toISOString()),
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
