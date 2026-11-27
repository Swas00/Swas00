# Stratosphere: cloud-computing profile for @Swas00

Everything on the profile is generated from live GitHub data by small Python scripts (standard library plus Pillow for the avatar), rebuilt every six hours by GitHub Actions. All visuals are pure SVG (SMIL), so they animate inside `<img>` on github.com.

## What's in it

| Section | Asset | Script | What it shows |
|:--|:--|:--|:--|
| Hero | `header.svg` | `banners.py` | Cloud-layer parallax sky, live service-mesh cluster, typed prompt, status chips, traffic wave over server racks |
| 01 Architecture | `architecture.svg` | `architecture.py` | Clients, edge, load balancer, autoscaling containers (your latest repos), data tier, CI/CD strip |
| 02 Cluster status | `cluster.svg` | `cluster.py` | Avatar node, repos, stars, followers, streak, language mix, 30-day pulse |
| 03 Observability | `observe.svg` | `observe.py` | Requests/day series, traffic by hour, 52-week heatmap |
| 04 Data center | `datacenter.svg` | `datacenter.py` | One isometric rack per week, one LED per day |
| 05 Service mesh | `neural.svg` | `neural.py` | Repos as microservices in language namespaces (keeps its filename: the CTF points at it) |
| 06 Deployments | `deploy.svg` + table | `deploy.py`, `explorer.py` | 30-day push timeline and the service catalog table |
| 07 Global edge | `edge.svg` | `edge.py` | Globe, 365-day ring, visitor nodes |
| 08 CTF | Hall of Fame | `ctf_verify.py` | Unchanged three-stage CTF |
| 09 Toolchain | `stack.svg` | `stack.py` | Layered stack; edit `LAYERS` in the script |

Design tokens (colours, type, helpers) live in `scripts/theme.py`.

## Rebuild locally with live data

```bash
GITHUB_TOKEN=$(gh auth token) ./scripts/build_all.sh
```

No token handy? `PREVIEW_DATA=1 ./scripts/build_all.sh` renders with placeholder contribution numbers so you can check layouts. `scripts/preview.py` writes `preview.html`, a single page showing every asset.

## Deploy

```bash
git add -A
git commit -m "feat: stratosphere cloud profile"
git push
```

In the repo settings, enable **Actions → General → Workflow permissions → Read and write**. Then run the "Update showcase" workflow once (Actions tab → Run workflow) so every chart picks up your real contribution data.

## Secrets and issue forms

* `CTF_FLAG` repo secret arms the CTF (unchanged).
* The "Add my node" issue form (`star.yml`) feeds `stars/visitors.json`; `stars.yml` redraws `edge.svg` on each new node.
