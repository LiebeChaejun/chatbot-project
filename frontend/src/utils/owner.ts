import { STORAGE_KEYS } from "../constants";

export function getOrCreateOwnerId(): string {
  let ownerId = localStorage.getItem(STORAGE_KEYS.OWNER_ID);
  if (!ownerId) {
    ownerId = crypto.randomUUID();
    localStorage.setItem(STORAGE_KEYS.OWNER_ID, ownerId);
  }
  return ownerId;
}
