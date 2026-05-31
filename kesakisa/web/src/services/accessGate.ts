import { API_BASE_URL } from './apiConfig'

export type AccessRole = 'player' | 'admin'

export interface AccessSession {
  role: AccessRole
  label: string
  teamId?: string | null
  token: string
  grantedAt: string
  expiresAt: string
}

export interface AccessResult {
  session: AccessSession | null
  error: string | null
}

export interface PlayerInvite {
  name: string
  label: string
  role: 'player'
  code: string
}

export interface PlayerInviteResult {
  invite: PlayerInvite | null
  error: string | null
}

const ACCESS_STORAGE_KEY = 'kesakisa-2026-access-session-v1'

export function loadAccessSession (requiredRole: AccessRole): AccessSession | null {
  const stored = window.localStorage.getItem(ACCESS_STORAGE_KEY)

  if (!stored) {
    return null
  }

  try {
    const parsed = JSON.parse(stored) as Partial<AccessSession>

    if (
      isRole(parsed.role) &&
      typeof parsed.label === 'string' &&
      typeof parsed.token === 'string' &&
      typeof parsed.grantedAt === 'string' &&
      typeof parsed.expiresAt === 'string' &&
      new Date(parsed.expiresAt).getTime() > Date.now() &&
      canAccess(requiredRole, parsed.role)
    ) {
      return parsed as AccessSession
    }
  } catch {
    clearAccessSession()
  }

  return null
}

export function saveAccessSession (session: AccessSession): void {
  window.localStorage.setItem(ACCESS_STORAGE_KEY, JSON.stringify(session))
}

export function clearAccessSession (): void {
  window.localStorage.removeItem(ACCESS_STORAGE_KEY)
}

export async function loginWithCode (code: string, requiredRole: AccessRole): Promise<AccessResult> {
  return requestSession('/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      code,
      requiredRole
    })
  }, requiredRole)
}

export async function validateAccessSession (session: AccessSession, requiredRole: AccessRole): Promise<AccessSession | null> {
  const result = await requestSession('/me', {
    headers: {
      Authorization: `Bearer ${session.token}`
    }
  }, requiredRole)

  return result.session
}

export async function createPlayerInvite (name: string, token: string): Promise<PlayerInviteResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/invite-code`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ name })
    })
    const payload = await response.json() as { data?: Partial<PlayerInvite>, message?: string }

    if (!response.ok || !payload.data || !isPlayerInvite(payload.data)) {
      return {
        invite: null,
        error: payload.message ?? 'Pelaajakoodia ei voitu luoda.'
      }
    }

    return {
      invite: payload.data,
      error: null
    }
  } catch {
    return {
      invite: null,
      error: 'Yhteys pelaajakoodin luontiin epäonnistui.'
    }
  }
}

async function requestSession (path: string, init: RequestInit, requiredRole: AccessRole): Promise<AccessResult> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, init)
    const payload = await response.json() as { data?: Partial<AccessSession>, message?: string }

    if (!response.ok || !payload.data || !isAccessSession(payload.data) || !canAccess(requiredRole, payload.data.role)) {
      return {
        session: null,
        error: payload.message ?? 'Koodia ei voitu vahvistaa.'
      }
    }

    return {
      session: payload.data,
      error: null
    }
  } catch {
    return {
      session: null,
      error: 'Yhteys kirjautumiseen epäonnistui.'
    }
  }
}

function isAccessSession (value: Partial<AccessSession>): value is AccessSession {
  return isRole(value.role) &&
    typeof value.label === 'string' &&
    typeof value.token === 'string' &&
    typeof value.grantedAt === 'string' &&
    typeof value.expiresAt === 'string'
}

function isPlayerInvite (value: Partial<PlayerInvite>): value is PlayerInvite {
  return value.role === 'player' &&
    typeof value.name === 'string' &&
    typeof value.label === 'string' &&
    typeof value.code === 'string'
}

function isRole (value: unknown): value is AccessRole {
  return value === 'player' || value === 'admin'
}

function canAccess (requiredRole: AccessRole, grantedRole: AccessRole): boolean {
  return grantedRole === 'admin' || requiredRole === grantedRole
}
