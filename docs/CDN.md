# CDN for Dashboard

## Vercel
Deploy to Vercel for automatic CDN and edge caching of static assets.

## Cloudflare
1. Add project to Cloudflare Pages
2. Static assets are cached at edge
3. Set cache headers in `next.config.ts` for `/api/status` etc.

## Custom
Set `Cache-Control` on static outputs:
- `_next/static/*`: immutable, 1 year
- `*.js`, `*.css`: public, 1 week
