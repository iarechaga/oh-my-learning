# Website Maintenance

The repository includes a self-contained static website under `website/` that renders
the Markdown lessons as browsable HTML pages. It is generated from the same source
files used for the learning workflow; the original `.md` files are never removed or
replaced.

## How it works

`website/build.py` scans the repository for lesson files that match the established
layout:

```
<domain>/<subject>/lessons/<NN>-<slug>.md
```

It reads each file's YAML front matter and emits:

- `website/dist/index.html` — list of domains.
- `website/dist/<domain>/index.html` — list of subjects in that domain.
- `website/dist/<domain>/<subject>/index.html` — list of lessons with seniority and
  completion badges.
- `website/dist/<domain>/<subject>/<NN>-<slug>.html` — rendered lesson content.
- `website/dist/manifest.json` — navigation data for search or debugging.

Because the site is built from the live filesystem, **new lessons are included
automatically** as soon as they follow the naming convention above and contain the
required front matter.

## Front matter the site uses

- `title` — shown in lists and at the top of the lesson page.
- `id` — displayed as a badge (e.g. `microservices-patterns/01`).
- `status` — `drafted` or `discussed`; drives the completion badge.
- `mastery` — empty until discussed, then `solid`, `partial`, `shaky`, or `not-yet`.
- `seniority` — `junior`, `mid`, `senior`, `staff`, or `principal`; shown as a colored
  badge.
- `source` — optional; shown under the lesson title.
- `prerequisites` — optional; rendered as badge list.

## Agent responsibilities

1. **Ensure dependencies are installed before building.** If `website/build.py` fails
   with a missing-package error, install them first:
   ```bash
   pip3 install -r website/requirements.txt
   ```
2. **After authoring a new lesson** (Workflow B), rebuild the site so the new lesson
   appears in the navigation:
   ```bash
   python3 website/build.py
   ```
3. **After recording a discussion** (Workflow C), rebuild the site so the updated
   `status` and `mastery` values are reflected in the subject index and lesson page.
4. **After adding a whole domain or subject**, no extra website work is required
   beyond the normal index/summary updates, as long as the folder structure follows
   `<domain>/<subject>/lessons/<NN>-<slug>.md`.
5. **Do not edit `website/dist/` by hand.** It is a generated artifact and is not
   committed unless the repo policy explicitly includes it.
6. **If the learner asks to view the site**, build it and then serve it:
   ```bash
   python3 website/serve.py --build
   ```
   Report the local URL (`http://localhost:8000` by default) and remind the learner to
   press Ctrl+C to stop the server.

## Running the site locally

Build once:

```bash
python website/build.py
python website/serve.py
```

Build before serving:

```bash
python website/serve.py --build
```

Serve on a different port:

```bash
python website/serve.py 3000
```

Live-reload while editing (requires `watchdog`):

```bash
python website/build.py --watch
```

## Dependencies

Install the Python dependencies first:

```bash
pip install -r website/requirements.txt
```

Required packages: Jinja2, Markdown, PyYAML, Pygments.
