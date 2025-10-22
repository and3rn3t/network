/**
 * UniFi Network API - Cloudflare Workers
 *
 * Main entry point for the API running on Cloudflare Workers with Hono framework.
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";

// Import routes
import alertRoutes from "./routes/alerts";
import analyticsRoutes from "./routes/analytics";
import authRoutes from "./routes/auth";
import channelRoutes from "./routes/channels";
import clientRoutes from "./routes/clients";
import deviceRoutes from "./routes/devices";
import healthRoutes from "./routes/health";
import ruleRoutes from "./routes/rules";
import websocketRoutes from "./routes/websocket";

// Environment bindings
export interface Env {
  DB: D1Database;
  CACHE: KVNamespace;
  WEBSOCKET: DurableObjectNamespace;
  JWT_SECRET: string;
  JWT_EXPIRATION: string;
  CORS_ORIGIN: string;
}

// Create Hono app
const app = new Hono<{ Bindings: Env }>();

// Middleware
app.use("*", logger());
app.use("*", prettyJSON());
app.use(
  "*",
  cors({
    origin: (origin) => origin, // Allow all origins in dev, restrict in production
    allowMethods: ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
    credentials: true,
  })
);

// Root endpoint
app.get("/", (c) => {
  return c.json({
    name: "UniFi Network API",
    version: "1.0.0",
    docs: "/docs",
    health: "/health",
    websocket: "/ws",
  });
});

// Mount routes
app.route("/health", healthRoutes);
app.route("/api/auth", authRoutes);
app.route("/api/alerts", alertRoutes);
app.route("/api/rules", ruleRoutes);
app.route("/api/channels", channelRoutes);
app.route("/api/devices", deviceRoutes);
app.route("/api/clients", clientRoutes);
app.route("/api/analytics", analyticsRoutes);
app.route("/ws", websocketRoutes);

// Error handling
app.onError((err, c) => {
  console.error("Error:", err);
  return c.json(
    {
      error: err.message || "Internal Server Error",
      status: "error",
    },
    500
  );
});

// 404 handler
app.notFound((c) => {
  return c.json(
    {
      error: "Not Found",
      path: c.req.path,
    },
    404
  );
});

// Export Durable Object for WebSocket
export { WebSocketDurableObject } from "./websocket/durable-object";

export default app;
