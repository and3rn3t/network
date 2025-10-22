import { Hono } from "hono";
import type { Env } from "../index";

const websocket = new Hono<{ Bindings: Env }>();

websocket.get("/", async (c) => {
  return c.json({ message: "WebSocket endpoint - coming soon" });
});

export default websocket;
