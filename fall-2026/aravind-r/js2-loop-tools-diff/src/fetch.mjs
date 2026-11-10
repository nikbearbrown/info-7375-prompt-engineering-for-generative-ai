// The only network code in the agent (CONTRACT.md, "Refuses"): one allow-listed
// host, https only, redirects refused rather than followed. Every attempt is logged.

export const ALLOWED_HOSTS = new Set(['boards-api.greenhouse.io']);

export class Refused extends Error {}

export function boardUrl(board) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(board ?? '')) throw new Refused(`board token "${board}" is not a plain Greenhouse token`);
  return `https://boards-api.greenhouse.io/v1/boards/${board}/jobs?content=true`;
}

export async function guardedFetch(url, { log = [], fetchImpl = globalThis.fetch } = {}) {
  const u = new URL(url);
  const entry = { at: new Date().toISOString(), url, host: u.host };
  log.push(entry);
  if (u.protocol !== 'https:' || !ALLOWED_HOSTS.has(u.host)) {
    entry.result = 'refused: host not on allow-list';
    throw new Refused(`refused ${u.host}: not on the allow-list (${[...ALLOWED_HOSTS].join(', ')})`);
  }
  const res = await fetchImpl(url, { redirect: 'manual', headers: { accept: 'application/json' } });
  entry.status = res.status;
  if (res.status >= 300 && res.status < 400) {
    entry.result = 'refused: redirect';
    throw new Refused(`refused redirect from ${u.host} (status ${res.status}) to ${res.headers?.get?.('location') ?? 'unknown'}`);
  }
  if (!res.ok) { entry.result = 'http error'; throw new Error(`HTTP ${res.status} from ${url}`); }
  entry.result = 'ok';
  return await res.text();
}
