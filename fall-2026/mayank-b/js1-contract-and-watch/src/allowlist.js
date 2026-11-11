// Every network request goes through allowedFetch (CONTRACT.md, Refuses, row 1).
import { ALLOWED_HOSTS } from "./config.js";

export class HostNotAllowedError extends Error {
  constructor(host) {
    super(`refused: host "${host}" is not on the allow-list (${ALLOWED_HOSTS.join(", ")}); nothing was fetched`);
    this.name = "HostNotAllowedError";
    this.host = host;
  }
}

export function assertAllowed(url) {
  const { protocol, hostname } = new URL(String(url));
  if (protocol !== "https:" || !ALLOWED_HOSTS.includes(hostname)) throw new HostNotAllowedError(hostname);
}

// `fetchImpl` is injectable so tests can prove a refused host never reaches the network.
export function makeAllowedFetch(fetchImpl = globalThis.fetch) {
  return async function allowedFetch(input, init) {
    assertAllowed(input instanceof Request ? input.url : input);
    return fetchImpl(input, init);
  };
}

export const allowedFetch = makeAllowedFetch();
