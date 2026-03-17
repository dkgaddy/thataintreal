# Website Design Recreation

## Workflow

When the user provides a reference image (screenshot) and optionally some CSS classes or style notes:

1. **Generate** a single `index.html` file using Tailwind CSS (via CDN). Include all content inline — no external files unless requested.
2. **Screenshot** the rendered page using Puppeteer (`npx puppeteer screenshot index.html --fullpage` or equivalent). If the page has distinct sections, capture those individually too.
3. **Compare** your screenshot against the reference image. Check for mismatches in:
   - Spacing and padding (measure in px)
   - Font sizes, weights, and line heights
   - Colors (exact hex values)
   - Alignment and positioning
   - Border radii, shadows, and effects
   - Responsive behavior
   - Image/icon sizing and placement
4. **Fix** every mismatch found. Edit the HTML/Tailwind code.
5. **Re-screenshot** and compare again.
6. **Repeat** steps 3–5 until the result is within ~2–3px of the reference everywhere.

Do NOT stop after one pass. Always do at least 2 comparison rounds. Only stop when the user says so or when no visible differences remain.

## Technical Defaults

- Use Tailwind CSS via CDN (`<script src="https://cdn.tailwindcss.com"></script>`)
- Use placeholder images from `https://placehold.co/` when source images aren't provided
- Mobile-first responsive design
- Single `index.html` file unless the user requests otherwise

## Rules

- Do not add features, sections, or content not present in the reference image
- Match the reference exactly — do not "improve" the design
- If the user provides CSS classes or style tokens, use them verbatim
- Keep code clean but don't over-abstract — inline Tailwind classes are fine
- When comparing screenshots, be specific about what's wrong (e.g., "heading is 32px but reference shows ~24px", "gap between cards is 16px but should be 24px")

## Local Dev Server
```bash
python3 -m http.server 8082
```
Then open http://localhost:8082

## Deployment

**Live URL:** https://thataintreal.explosiveconcepts.com

**Server:**
- Host: ssh.explosiveconcepts.com
- Port: 18765
- User: u303-2kknmnzzzr45
- SSH key: `~/.ssh/explosiveconcepts_key` *(must be present on the device — key is not stored in this repo)*
- Document root: `~/www/thataintreal.explosiveconcepts.com/public_html`

**Deploy command** (git pull on server):
```bash
ssh -i ~/.ssh/explosiveconcepts_key -p 18765 u303-2kknmnzzzr45@ssh.explosiveconcepts.com \
  "cd ~/www/thataintreal.explosiveconcepts.com/public_html && git pull"
```

To deploy, just tell Claude: **"deploy thataintreal"**

> Note: The SSH key passphrase is not stored anywhere — you will be prompted to enter it.
> To avoid repeated prompts in a session, run `ssh-add ~/.ssh/explosiveconcepts_key` first.
