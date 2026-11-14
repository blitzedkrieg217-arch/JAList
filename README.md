# Japan 2027 Packing List

Continued from the existing JAList `index.html` on main (blob 29698f7c6a85119dab1b3fb818d3472177484b78). All 51 initial entries, quantities, research flags, and nested items are preserved.

Private GPT Site: https://japan-packing-2027.nschmidgall.chatgpt.site

The app uses dispatch-owned ChatGPT sign-in, an owner-only Site access policy, and server-side D1 records keyed by authenticated Site user ID. Browser code contains no credentials. Each API operation requires identity; writes also validate Origin. The D1 schema is applied through tracked Drizzle migrations.

Edits automatically save after 600 ms. Open devices poll every 5 seconds and refresh on focus. Item-level operations merge unrelated concurrent edits; simultaneous edits to the same field use the last accepted write. Revision checks prevent lost database updates and request IDs make retries idempotent. Failed requests retry while the page remains open; closing with unsaved changes triggers a browser warning. Saved data survives browser-storage deletion.

Source: `app/packing-html.ts` retains the existing application UI, `app/api/list/route.ts` implements persistence, and `db/seed.ts` preserves the original list. `index.html` is the matching UI source for reference; it requires the GPT Site backend and cannot synchronize through GitHub Pages alone. The previous GitHub-token sync has been removed from the active app.

Run `node --experimental-strip-types verify.mjs` for list and operation checks. Build with `npm run build`. Publish through Sites from the exact source commit. No API key is required.
