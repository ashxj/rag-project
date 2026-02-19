# RAG Meklesanas Simulators

Minimals macibu projekts ar Python backend un frontend, kas imite RAG meklešanu pa teksta datiem.

## Kas ir realizets

- API kategoriju iegusanai no `data/` apaksmapem
- API meklešanai pa izveleto kategoriju vai pa visam kategorijam
- Meklesana pa teksta dalam (chunk)
- Vienkarsa rezultatu ranžesana pec tokenu sakritibas
- Pielaide latviesu diakritikai (`ā/a`, `ē/e`, `š/s` u.c.)
- Atrasto vārdu izcelsana frontend dalā

## Kas izmantots

- Python 3
- FastAPI
- Uvicorn
- HTML/CSS/JavaScript (bez framework)

## Struktura

- `app/main.py` — FastAPI lietotne un HTTP endpointi
- `app/rag.py` — chunk sadalisanas un meklešanas logika
- `static/` — meklešanas interfeiss
- `data/` — tekstu baze pa prieksmetiem (`math`, `physic`, `programming`)

## API

- `GET /api/categories` — pieejamo kategoriju saraksts
- `POST /api/search` — meklešana

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Atvert parluka: `http://127.0.0.1:8000`
