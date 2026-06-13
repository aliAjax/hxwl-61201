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

### 烧制批次

- `GET /health`
- `POST /batches`
- `GET /batches`
- `GET /batches/{batch_id}`
- `PATCH /batches/{batch_id}/result`
- `DELETE /batches/{batch_id}`
- `GET /works/{work_code}/history`

### 材料字典

- `POST /materials` - 新增材料
- `GET /materials` - 材料列表（可选 `?category=clay|glaze` 筛选）
- `DELETE /materials/{material_id}` - 删除材料

**材料字段说明**

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| `name` | string | 材料名称 |
| `category` | string | 分类：`clay`（泥料）或 `glaze`（釉料） |
| `id` | int | 材料ID |
| `created_at` | string | 创建时间 |

**创建材料示例**

```bash
# 新增泥料
curl -X POST http://localhost:61201/materials \
  -H "Content-Type: application/json" \
  -d '{"name": "紫砂泥", "category": "clay"}'

# 新增釉料
curl -X POST http://localhost:61201/materials \
  -H "Content-Type: application/json" \
  -d '{"name": "天青釉", "category": "glaze"}'

# 查看所有材料
curl http://localhost:61201/materials

# 只看泥料
curl "http://localhost:61201/materials?category=clay"

# 删除材料
curl -X DELETE http://localhost:61201/materials/1
```

> **注意**：创建烧制批次时，`clay` 和 `glaze` 字段仍支持自由文本输入，不强制绑定材料字典。
