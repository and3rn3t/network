import { Hono } from "hono";
import type { Env } from "../index";

const devices = new Hono<{ Bindings: Env }>();

devices.get("/", async (c) => {
  return c.json({ message: "Devices endpoint - coming soon" });
});

export default devices;
