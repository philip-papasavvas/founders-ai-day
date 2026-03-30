# Founders AI Day

## Repository structure

This repo contains demo projects built during Founders AI Day. Each project lives in its own directory at the repo root.

## Netlify deployment

The site is deployed to Netlify at `https://founders-ai-day-demos.netlify.app/`.

- **Publish directory**: `site`
- **Site name**: `founders-ai-day-demos`

### How the site directory works

```
site/
  index.html                ← landing page listing all demos
  meal-planning/
    index.html              ← Meal Planning Amp demo
  <new-demo>/
    index.html              ← add new demos as subdirectories here
```

Each demo gets its own subdirectory under `site/`. The landing page at `site/index.html` links to all demos.

### Adding a new demo

1. Create a directory under `site/` (e.g. `site/my-new-demo/`)
2. Put an `index.html` (and any assets) in that directory
3. Add a card linking to `/my-new-demo/` in `site/index.html` — follow the existing `<a class="demo-card">` pattern
4. Commit and push — Netlify auto-deploys from `main`

### Design system

The landing page and existing demos use a shared visual style:
- Fonts: Cormorant Garamond (headings), IBM Plex Sans (body)
- Palette: plum (`#4f2740`), berry (`#bf4f77`), rosewood (`#7f3557`), muted (`#735865`), ink (`#34232d`)
- Cards: `border-radius: 22px`, `box-shadow: 0 18px 38px rgba(105,56,79,0.12)`, semi-transparent white background
- Badges/pills: `border-radius: 999px`, berry-tinted backgrounds

## Existing demos

- **meal_planning_amp/** — Streamlit meal planning app (source code)
- **site/meal-planning/** — Static HTML version of the meal planner, deployed to Netlify