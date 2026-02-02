import re

REQUIRED_HEADINGS = [
    "▼案件情報",
    "【1枚目】管理DD（一次資料ベース）",
    "【2枚目】リノベ制限チェック（事故防止）",
]


def test_headings_order_snapshot():
    sample = """
▼案件情報
- 物件名：未指定

========================
【1枚目】管理DD（一次資料ベース）
1) まず結論（3行で）

========================
【2枚目】リノベ制限チェック（事故防止）
0) まず結論（2行）
"""
    positions = [sample.find(h) for h in REQUIRED_HEADINGS]
    assert all(pos != -1 for pos in positions)
    assert positions == sorted(positions)


def test_only_bracketed_refs():
    sample = "根拠は【重調p2】【規約p不明：第1条／境界】"
    invalid = re.findall(r"\[[^\]]+\]", sample)
    assert invalid == []
