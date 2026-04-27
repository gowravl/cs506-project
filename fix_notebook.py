import json, sys

with open('models.ipynb', 'r', encoding='utf-8') as f:
    nb = json.load(f)

changed = 0
for cell in nb['cells']:
    if cell.get('id') != 'decefaef':
        continue

    src = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])

    if 'resp_lag7' in src:
        print('Already updated — nothing to do.')
        sys.exit(0)

    # Insert lag computation after year_trend line
    insert_after = "features['year_trend'] = (features['date'] - features['date'].min()).dt.days / 365.25\n"
    lag_block = (
        "\n"
        "for lag in [7, 14, 30]:\n"
        "    features[f'resp_lag{lag}'] = features['pct_respiratory'].shift(lag)\n"
        "features = features.dropna().reset_index(drop=True)\n"
    )
    src = src.replace(insert_after, insert_after + lag_block)

    # Extend LINEAR_FEATURES
    src = src.replace(
        "    'month_sin', 'month_cos', 'day_of_week', 'is_weekend', 'year_trend',\n]",
        "    'month_sin', 'month_cos', 'day_of_week', 'is_weekend', 'year_trend',\n    'resp_lag7', 'resp_lag14', 'resp_lag30',\n]"
    )

    # Extend TREE_FEATURES
    src = src.replace(
        "    'month', 'day_of_week', 'is_weekend', 'season_num', 'year_trend',\n]",
        "    'month', 'day_of_week', 'is_weekend', 'season_num', 'year_trend',\n    'resp_lag7', 'resp_lag14', 'resp_lag30',\n]"
    )

    # Fix print statement
    src = src.replace(
        "print(f'Dataset: {features.shape[0]} rows')",
        "print(f'Dataset: {features.shape[0]} rows (30 dropped for autoregressive lags)')"
    )

    cell['source'] = src.splitlines(keepends=True)
    changed += 1
    break

if changed == 0:
    print('ERROR: setup cell not found.')
    sys.exit(1)

with open('models.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Done. Restart the kernel and Run All.')
