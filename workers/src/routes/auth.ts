/**
 * Authentication endpoints
 */

import { zValidator } from "@hono/zod-validator";
import bcrypt from "bcryptjs";
import { Hono } from "hono";
import * as jose from "jose";
import { z } from "zod";
import type { Env } from "../index";

const auth = new Hono<{ Bindings: Env }>();

// Validation schemas
const loginSchema = z.object({
  username: z.string().min(3),
  password: z.string().min(6),
});

const registerSchema = z.object({
  username: z.string().min(3),
  email: z.string().email(),
  password: z.string().min(6),
  full_name: z.string().optional(),
});

// Helper to create JWT token
async function createToken(
  userId: number,
  username: string,
  secret: string
): Promise<string> {
  const secretKey = new TextEncoder().encode(secret);

  const token = await new jose.SignJWT({ userId, username })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("7d")
    .sign(secretKey);

  return token;
}

// Helper to verify JWT token
export async function verifyToken(token: string, secret: string) {
  try {
    const secretKey = new TextEncoder().encode(secret);
    const { payload } = await jose.jwtVerify(token, secretKey);
    return payload;
  } catch {
    return null;
  }
}

// Login endpoint
auth.post("/login", zValidator("json", loginSchema), async (c) => {
  const { username, password } = c.req.valid("json");

  try {
    // Find user by username
    const user = await c.env.DB.prepare(
      "SELECT * FROM users WHERE username = ?"
    )
      .bind(username)
      .first();

    if (!user) {
      return c.json({ error: "Invalid credentials" }, 401);
    }

    // Verify password
    const valid = await bcrypt.compare(
      password,
      user.hashed_password as string
    );
    if (!valid) {
      return c.json({ error: "Invalid credentials" }, 401);
    }

    // Check if user is active
    if (!user.is_active) {
      return c.json({ error: "Account is inactive" }, 403);
    }

    // Update last login
    await c.env.DB.prepare(
      "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?"
    )
      .bind(user.id)
      .run();

    // Create token
    const token = await createToken(
      user.id as number,
      user.username as string,
      c.env.JWT_SECRET
    );

    return c.json({
      access_token: token,
      token_type: "Bearer",
      expires_in: 604800, // 7 days in seconds
      user: {
        id: user.id,
        username: user.username,
        email: user.email,
        full_name: user.full_name,
        is_superuser: user.is_superuser,
      },
    });
  } catch (error) {
    console.error("Login error:", error);
    return c.json({ error: "Login failed" }, 500);
  }
});

// Register endpoint
auth.post("/register", zValidator("json", registerSchema), async (c) => {
  const { username, email, password, full_name } = c.req.valid("json");

  try {
    // Check if username exists
    const existing = await c.env.DB.prepare(
      "SELECT id FROM users WHERE username = ? OR email = ?"
    )
      .bind(username, email)
      .first();

    if (existing) {
      return c.json({ error: "Username or email already exists" }, 409);
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 10);

    // Create user
    const result = await c.env.DB.prepare(
      `INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser)
       VALUES (?, ?, ?, ?, 1, 0)`
    )
      .bind(username, email, hashedPassword, full_name || null)
      .run();

    // Get created user
    const user = await c.env.DB.prepare("SELECT * FROM users WHERE id = ?")
      .bind(result.meta.last_row_id)
      .first();

    return c.json(
      {
        id: user?.id,
        username: user?.username,
        email: user?.email,
        full_name: user?.full_name,
        created_at: user?.created_at,
      },
      201
    );
  } catch (error) {
    console.error("Register error:", error);
    return c.json({ error: "Registration failed" }, 500);
  }
});

// Get current user
auth.get("/me", async (c) => {
  const authHeader = c.req.header("Authorization");

  if (!authHeader?.startsWith("Bearer ")) {
    return c.json({ error: "Missing or invalid authorization header" }, 401);
  }

  const token = authHeader.substring(7);
  const payload = await verifyToken(token, c.env.JWT_SECRET);

  if (!payload) {
    return c.json({ error: "Invalid token" }, 401);
  }

  try {
    const user = await c.env.DB.prepare(
      "SELECT id, username, email, full_name, is_active, is_superuser, created_at, last_login FROM users WHERE id = ?"
    )
      .bind(payload.userId)
      .first();

    if (!user) {
      return c.json({ error: "User not found" }, 404);
    }

    return c.json(user);
  } catch (error) {
    console.error("Get user error:", error);
    return c.json({ error: "Failed to get user" }, 500);
  }
});

export default auth;
