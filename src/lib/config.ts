/**
 * FlagRank Application Configuration
 *
 * Resolves the backend API base URL based on environment settings:
 * 1. Explicit VITE_API_BASE_URL environment variable if provided.
 * 2. In development (import.meta.env.DEV), defaults to 'http://127.0.0.1:8000'.
 * 3. In production, defaults to empty string '' (allowing same-origin / reverse proxy routing).
 */
const envBaseUrl = import.meta.env.VITE_API_BASE_URL;

export const API_BASE_URL = typeof envBaseUrl === 'string'
  ? envBaseUrl.replace(/\/+$/, '')
  : (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '');

/**
 * Returns a fully qualified API endpoint URL.
 */
export function getApiUrl(path: string): string {
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${cleanPath}`;
}
