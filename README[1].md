
# Mobina Nail Studio – One‑Page Site (DE/EN/FA)

This is a **ready-to-host** static website for a nail studio, with **multi-language support (Deutsch/English/فارسی)**, a **scripted chatbot**, and easy content editing via `content.json`.

## Files
- `index.html` – main page (Tailwind from CDN; no build step needed)
- `content.json` – all text, labels, and image names (DE/EN/FA)
- `assets/js/app.js` – renders content and handles the chatbot + language switch
- `assets/css/style.css` – tiny extra styles
- `images/` – placeholder images (replace with real photos later)

## Edit Content
- Update texts or bullet points in `content.json` (for each language section).
- Replace images in `images/` **with the same file names**, or change the file names inside `content.json`.

## Deploy to GitHub Pages
1. Create a new GitHub repo, e.g., `mobina-nails`.
2. Upload all files/folders exactly as they are.
3. In **Settings → Pages**, set:
   - Source: **Deploy from a branch**
   - Branch: **main** (or master) and **/ (root)**
4. The site will be available at `https://YOUR-USER.github.io/mobina-nails/`.

## Custom Domain
- Buy a domain (e.g., from Namecheap, IONOS, etc.).
- In your repo, create a file named `CNAME` (no extension) with **only** your domain inside, e.g.:
  ```
  mobina-nails.de
  ```
- Add DNS **CNAME** record at your domain provider to point `www` → `YOUR-USER.github.io`.
- (Optional) For apex (`@`) use ALIAS/ANAME if supported, or redirect apex → `www`.

## Notes
- No private API keys are included. The chatbot is scripted (no server/backend required).
- For a real AI chatbot later, use a small server or serverless function and keep keys on the server.
- License for placeholder images: **you created them locally; feel free to replace with your own photos**.
