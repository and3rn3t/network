/**
 * Health check endpoints
 */

import { Hono } from 'hono';
import type { Env } from '../index';

const health = new Hono<{ Bindings: Env }>();

health.get('/', async (c) => {
  return c.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    version: '1.0.0',
  });
});

health.get('/ready', async (c) => {
  try {
    // Check database connection
    const result = await c.env.DB.prepare('SELECT 1').first();
    
    return c.json({
      status: 'ready',
      database: 'connected',
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    return c.json({
      status: 'not ready',
      database: 'disconnected',
      error: error instanceof Error ? error.message : 'Unknown error',
    }, 503);
  }
});

export default health;
