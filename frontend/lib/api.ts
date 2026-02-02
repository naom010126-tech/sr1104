const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export async function createCase(name?: string) {
  const res = await fetch(`${API_BASE}/cases`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: name || null }),
  });
  if (!res.ok) {
    throw new Error("案件作成に失敗しました");
  }
  return res.json();
}

export async function uploadDocument(caseId: number, docType: string, file: File) {
  const form = new FormData();
  form.append("doc_type", docType);
  form.append("file", file);

  const res = await fetch(`${API_BASE}/cases/${caseId}/documents`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) {
    throw new Error("アップロードに失敗しました");
  }
  return res.json();
}

export async function analyzeCase(caseId: number) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("解析に失敗しました");
  }
  return res.json();
}

export async function generateReport(caseId: number) {
  const res = await fetch(`${API_BASE}/cases/${caseId}/generate-report`, {
    method: "POST",
  });
  if (!res.ok) {
    throw new Error("レポ生成に失敗しました");
  }
  return res.json();
}

export async function getCase(caseId: number) {
  const res = await fetch(`${API_BASE}/cases/${caseId}`);
  if (!res.ok) {
    throw new Error("案件取得に失敗しました");
  }
  return res.json();
}

export function reportPdfUrl(caseId: number) {
  return `${API_BASE}/cases/${caseId}/report.pdf`;
}
