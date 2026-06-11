# hxwl-61201

Python FastAPI后端：小型陶艺工作室窑炉烧制记录。

## Port

61201

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 61201 --reload
```

## API

- `GET /health`
- `POST /batches`
- `GET /batches`
- `GET /batches/{batch_id}`
- `PATCH /batches/{batch_id}/result`
- `DELETE /batches/{batch_id}`
- `GET /works/{work_code}/history`
