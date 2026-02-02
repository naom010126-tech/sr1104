from app.services.metrics_extraction import PageRecord


def test_page_ref_is_one_based():
    record = PageRecord(doc_type="重調", page_index=0, text="")
    assert record.ref() == "【重調p1】"
