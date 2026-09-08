# Kosh — dictionary everywhere + saved-word review

5 files, no build step, no API key, no cost (uses the free dictionaryapi.dev).

## What it does
- **Lookup tab**: search a word, see definitions/synonyms/audio (English or Hindi).
- **Share sheet**: install the PWA, then select text in any app → Share → Kosh. It pulls the first word out and looks it up automatically.
- **Saved tab**: save words, filter them, tap a row to read the full entry later (works offline — cached in localStorage).
- **Review**: Leitner-style flashcards (boxes 1–5, 0/1/3/7/14-day intervals) for words that are due.

## Deploy (phone, no terminal)
**Netlify Drop** — fastest:
1. Zip these 5 files (or use a phone file-manager app that can zip a folder) — actually Netlify Drop also accepts an unzipped folder on desktop, but on mobile it's easier to drag a `.zip`.
2. Go to app.netlify.com/drop, upload it. Done — you get an HTTPS URL immediately (share_target needs HTTPS).

**GitHub Pages** — if you want a repo:
1. New repo → Add file → upload all 5 files at the root.
2. Settings → Pages → deploy from `main` / root.
3. Open the `github.io` URL on your phone, tap "Add to Home Screen" / install prompt.

## Notes
- Share target only works once the PWA is **installed** (Add to Home Screen), and only on Android/Chrome — iOS Safari doesn't support Web Share Target yet, so on iPhone you'd paste into the search box instead.
- Icons are inline SVG (no image generation used) — swap `icon.svg` / `icon-maskable.svg` for your own art anytime, no code changes needed.
- All saved words + review state live in `localStorage` on-device — nothing is sent anywhere except the dictionary lookup itself.
