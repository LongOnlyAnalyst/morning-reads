# morning-reads
A static page of substantive, current market, macro, and tech reading for Zane's morning, which takes about 3 hours to get through.

- `items.json`: the current list. Each item has title, source, date (publication date), min (read time), url, why (2 sentences), plus optional `top` and `paywall`.
- `template.html`: the page shell (dark theme, no external dependencies). `build.py` embeds the items into `index.html`.
- `history.json`: every item ever listed (url, title, source, date, listedOn, status: top/listed/expired).
- Read state lives in the browser's localStorage under `mr-read:<url>`.

Refresh: edit `items.json`, run `python3 build.py YYYY-MM-DD`, then commit and push. Full steps are in REFRESH.md. Netlify publishes from the repo root.
