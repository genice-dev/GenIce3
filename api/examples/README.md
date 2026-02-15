# /generate 入力例

## 最小構成（Ice Ih 2×2×2）

```json
{
  "unitcell": "1h",
  "rep": [2, 2, 2]
}
```

## オプション付き（A15 クラスレート）

```json
{
  "unitcell": "A15",
  "rep": [2, 2, 2],
  "unitcell_options": {
    "shift": [0.1, 0.1, 0.1],
    "density": 0.8,
    "assess_cages": true
  },
  "seed": 42
}
```

## curl での実行例

```bash
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d @api/examples/generate_request_minimal.json
```

## 主な単位胞名

| 名前   | 説明          |
|--------|---------------|
| 1h     | Ice Ih        |
| ice1h  | Ice Ih        |
| 4      | Ice IV        |
| A15    | A15 クラスレート |
| CS1    | CS1 クラスレート |
| HS1    | HS1 クラスレート |

## unitcell_options の主な項目

| 項目           | 型     | 説明                          |
|----------------|--------|-------------------------------|
| shift          | [x,y,z]| 分数座標のシフト              |
| density        | float  | 密度 (g/cm³)                  |
| assess_cages   | bool   | ケージ評価を行うか（クラスレート用） |
