import { Hono } from "hono";
import type { Env } from "../index";

const analytics = new Hono<{ Bindings: Env }>();

analytics.get("/", async (c) => {
  return c.json({ message: "Analytics endpoint - coming soon" });
});

export default analytics;
