# UniFi Network API - Cloudflare Workers Deployment

This directory contains the TypeScript/Hono API that runs on Cloudflare Workers.

## Architecture

- **Framework**: Hono (lightweight, fast)
- **Runtime**: Cloudflare Workers
- **Database**: Cloudflare D1 (SQLite)
- **Cache**: Cloudflare KV
- **WebSocket**: Durable Objects

## Setup

### 1. Install Dependencies

```powershell
cd workers
npm install
```

### 2. Create Cloudflare Resources

```powershell
# Create D1 database
wrangler d1 create network-db

# Create KV namespace
wrangler kv:namespace create CACHE

# Update wrangler.toml with the IDs returned
```

### 3. Initialize Database

```powershell
# Apply schema
wrangler d1 execute network-db --file=schema.sql
```

### 4. Set Secrets

```powershell
# Set JWT secret (generate a secure random string)
wrangler secret put JWT_SECRET

# If integrating with UniFi
wrangler secret put UNIFI_API_KEY
```

### 5. Deploy

```powershell
# Deploy to Cloudflare
wrangler deploy

# Or use npm script
npm run deploy
```

## Development

```powershell
# Run locally
npm run dev

# Type check
npm run type-check
```

## API Endpoints

### Health

- `GET /health` - Health check
- `GET /health/ready` - Readiness check

### Authentication

- `POST /api/auth/login` - Login
- `POST /api/auth/register` - Register
- `GET /api/auth/me` - Get current user

### Alerts

- `GET /api/alerts` - List alerts
- `GET /api/alerts/:id` - Get alert
- `POST /api/alerts/:id/acknowledge` - Acknowledge
- `POST /api/alerts/:id/resolve` - Resolve
- `GET /api/alerts/stats/summary` - Stats

### Rules

- `GET /api/rules` - List rules
- `GET /api/rules/:id` - Get rule
- `POST /api/rules` - Create rule
- `PUT /api/rules/:id` - Update rule
- `DELETE /api/rules/:id` - Delete rule

### Channels

- `GET /api/channels` - List channels
- `GET /api/channels/:id` - Get channel
- `POST /api/channels` - Create channel
- `PUT /api/channels/:id` - Update channel
- `DELETE /api/channels/:id` - Delete channel
- `POST /api/channels/:id/test` - Test channel

### WebSocket

- `GET /ws` - WebSocket connection

## Custom Domain

Add `api.andernet.dev` in Cloudflare Workers dashboard:

1. Go to Workers & Pages → network-api
2. Click "Custom Domains"
3. Add `api.andernet.dev`
4. DNS records will be created automatically

## Environment Variables

Set in `wrangler.toml` or as secrets:

- `JWT_SECRET` - Secret for JWT tokens (use secret)
- `JWT_EXPIRATION` - Token expiration time (default: 7d)
- `CORS_ORIGIN` - Allowed CORS origin (default: https://net.andernet.dev)

## Database Migrations

To update the database schema:

```powershell
# Create migration SQL file
# migrations/001_add_column.sql

# Apply migration
wrangler d1 execute network-db --file=migrations/001_add_column.sql
```

## Monitoring

View logs:

```powershell
wrangler tail network-api
```

## Default Credentials

**⚠️ CHANGE IMMEDIATELY IN PRODUCTION!**

- Username: `admin`
- Password: `admin123`

## Testing

```powershell
# Test health endpoint
curl https://api.andernet.dev/health

# Test login
curl -X POST https://api.andernet.dev/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```
