from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Dict, Any, List

DOC_LABELS = {
    "重調": "重調",
    "工事": "工事",
    "規約": "規約",
    "細則": "細則",
    "長修": "長修",
}


@dataclass
class PageRecord:
    doc_type: str
    page_index: int
    text: str

    def ref(self) -> str:
        label = DOC_LABELS.get(self.doc_type, self.doc_type)
        return f"【{label}p{self.page_index + 1}】"


def normalize(text: str) -> str:
    return text.replace(" ", "").replace("　", "")


def parse_number(value: str) -> Optional[float]:
    if value is None:
        return None
    trans_table = str.maketrans(
        {
            "０": "0",
            "１": "1",
            "２": "2",
            "３": "3",
            "４": "4",
            "５": "5",
            "６": "6",
            "７": "7",
            "８": "8",
            "９": "9",
            "．": ".",
            "，": ",",
        }
    )
    cleaned = value.translate(trans_table)
    cleaned = cleaned.replace(",", "").replace("円", "").replace("％", "").replace("%", "")
    cleaned = cleaned.replace("㎡", "")
    cleaned = cleaned.replace("m2", "").replace("m²", "")
    cleaned = cleaned.replace("万", "0000")
    cleaned = cleaned.replace("千", "000")
    cleaned = cleaned.replace("億", "00000000")
    cleaned = cleaned.strip()
    if not cleaned:
        return None
    try:
        return float(cleaned)
    except ValueError:
        return None


def find_first(patterns: List[re.Pattern[str]], text: str) -> Optional[str]:
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def extract_metrics(pages: List[PageRecord]) -> Dict[str, Any]:
    metrics: Dict[str, Any] = {
        "management_fee": {"value_yen_per_month": None, "page_ref": None},
        "reserve_fee": {"value_yen_per_month": None, "page_ref": None},
        "unit_area_m2": {"value": None, "page_ref": None},
        "reserve_balance": {"value_yen": None, "page_ref": None},
        "arrears": {"value_yen": None, "count": None, "max_months": None, "page_ref": None},
        "loan": {"exists": None, "balance_yen": None, "interest_rate": None, "page_ref": None},
        "step_increase": {"exists": None, "details": None, "page_ref": None},
        "major_repairs": [],
    }

    management_patterns = [
        re.compile(r"管理費[^0-9]*(\d[\d,]*)(?:円|円/月|円／月|円月)?"),
    ]
    reserve_patterns = [
        re.compile(r"修繕積立金[^0-9]*(\d[\d,]*)(?:円|円/月|円／月|円月)?"),
    ]
    area_patterns = [
        re.compile(r"専有面積[^0-9]*(\d+[\d,\.]*)(?:㎡|m2|m²)"),
    ]
    balance_patterns = [
        re.compile(r"修繕積立金残高[^0-9]*(\d[\d,]*)"),
        re.compile(r"積立金残高[^0-9]*(\d[\d,]*)"),
    ]
    arrears_amount_patterns = [
        re.compile(r"滞納[^0-9]*(\d[\d,]*)"),
    ]
    arrears_count_patterns = [
        re.compile(r"滞納.*?(\d+)件"),
    ]
    arrears_month_patterns = [
        re.compile(r"滞納.*?(\d+)ヶ月"),
        re.compile(r"滞納.*?(\d+)か月"),
    ]
    loan_patterns = [
        re.compile(r"借入金[^0-9]*(\d[\d,]*)"),
        re.compile(r"借入残高[^0-9]*(\d[\d,]*)"),
    ]
    interest_patterns = [
        re.compile(r"金利[^0-9]*(\d+[\d\.]*)%"),
    ]
    step_patterns = [
        re.compile(r"段階増額.*?(\d[\d,]*)"),
        re.compile(r"増額予定"),
    ]

    for page in pages:
        text = normalize(page.text)
        if metrics["management_fee"]["value_yen_per_month"] is None:
            raw = find_first(management_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["management_fee"] = {
                    "value_yen_per_month": int(value),
                    "page_ref": page.ref(),
                }
        if metrics["reserve_fee"]["value_yen_per_month"] is None:
            raw = find_first(reserve_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["reserve_fee"] = {
                    "value_yen_per_month": int(value),
                    "page_ref": page.ref(),
                }
        if metrics["unit_area_m2"]["value"] is None:
            raw = find_first(area_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["unit_area_m2"] = {
                    "value": value,
                    "page_ref": page.ref(),
                }
        if metrics["reserve_balance"]["value_yen"] is None:
            raw = find_first(balance_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["reserve_balance"] = {
                    "value_yen": int(value),
                    "page_ref": page.ref(),
                }
        if metrics["arrears"]["value_yen"] is None:
            raw = find_first(arrears_amount_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["arrears"]["value_yen"] = int(value)
                metrics["arrears"]["page_ref"] = page.ref()
        if metrics["arrears"]["count"] is None:
            raw = find_first(arrears_count_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["arrears"]["count"] = int(value)
                metrics["arrears"]["page_ref"] = page.ref()
        if metrics["arrears"]["max_months"] is None:
            raw = find_first(arrears_month_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["arrears"]["max_months"] = int(value)
                metrics["arrears"]["page_ref"] = page.ref()
        if metrics["loan"]["balance_yen"] is None:
            raw = find_first(loan_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["loan"]["exists"] = True
                metrics["loan"]["balance_yen"] = int(value)
                metrics["loan"]["page_ref"] = page.ref()
        if metrics["loan"]["interest_rate"] is None:
            raw = find_first(interest_patterns, text)
            value = parse_number(raw)
            if value:
                metrics["loan"]["interest_rate"] = value
                if metrics["loan"]["page_ref"] is None:
                    metrics["loan"]["page_ref"] = page.ref()
        if metrics["step_increase"]["exists"] is None:
            raw = find_first(step_patterns, text)
            if raw:
                metrics["step_increase"] = {
                    "exists": True,
                    "details": raw,
                    "page_ref": page.ref(),
                }

        if page.doc_type in {"工事", "長修"}:
            for match in re.finditer(r"(19|20)\d{2}年", text):
                year = int(match.group(0).replace("年", ""))
                metrics["major_repairs"].append({
                    "year": year,
                    "desc": "工事履歴",
                    "page_ref": page.ref(),
                })

    if metrics["loan"]["exists"] is None:
        metrics["loan"]["exists"] = False

    return metrics


def compute_values(metrics: Dict[str, Any]) -> Dict[str, Any]:
    reserve_fee = metrics.get("reserve_fee", {}).get("value_yen_per_month")
    unit_area = metrics.get("unit_area_m2", {}).get("value")
    reserve_unit = None
    if reserve_fee and unit_area:
        reserve_unit = reserve_fee / unit_area

    major_repairs = metrics.get("major_repairs", [])
    years = sorted({entry["year"] for entry in major_repairs})
    intervals = []
    for i in range(1, len(years)):
        intervals.append(years[i] - years[i - 1])

    return {
        "reserve_unit_yen_per_m2": reserve_unit,
        "major_repair_years": years,
        "major_repair_intervals": intervals,
    }
