import type { AppState } from '../types'
import { API_BASE_URL } from './apiConfig'
import { normalizeState, remoteStatePayload } from './localStore'

interface StatePayload {
  data?: {
    state?: Partial<AppState> | null
  }
  message?: string
}

export interface RemoteStateResult {
  state: AppState | null
  error: string | null
}

export async function loadRemoteState (token: string): Promise<RemoteStateResult> {
  try {
    const response = await fetch(`${API_BASE_URL}/state`, {
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    const payload = await response.json() as StatePayload

    if (!response.ok) {
      return {
        state: null,
        error: payload.message ?? 'Jaettua pelitilaa ei voitu hakea.'
      }
    }

    if (!payload.data?.state) {
      return {
        state: null,
        error: null
      }
    }

    return {
      state: normalizeState(payload.data.state),
      error: null
    }
  } catch {
    return {
      state: null,
      error: 'Yhteys jaettuun pelitilaan epäonnistui.'
    }
  }
}

export async function saveRemoteState (state: AppState, token: string): Promise<string | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/state`, {
      method: 'PUT',
      cache: 'no-store',
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        state: remoteStatePayload(state)
      })
    })
    const payload = await response.json() as StatePayload

    if (!response.ok) {
      return payload.message ?? 'Jaettua pelitilaa ei voitu tallentaa.'
    }

    return null
  } catch {
    return 'Yhteys jaetun pelitilan tallennukseen epäonnistui.'
  }
}
