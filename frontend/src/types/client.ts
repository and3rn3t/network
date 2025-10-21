/**
 * Client types
 */

export interface Client {
  mac: string;
  hostname?: string | null;
  name?: string | null;
  ip?: string | null;
  blocked?: boolean;
  last_seen?: string | null;
}
