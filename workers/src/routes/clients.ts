import { Hono } from "hono";
import type { Env } from "../index";

const clients = new Hono<{ Bindings: Env }>();

clients.get("/", async (c) => {
  return c.json({ message: "Clients endpoint - coming soon" });
});

export default clients;
