"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { createCase, analyzeCase, generateReport, getCase, reportPdfUrl } from "../lib/api";
import DocumentUploader from "../components/DocumentUploader";

type CaseFormValues = {
  name: string;
};

export default function Home() {
  const [caseId, setCaseId] = useState<number | null>(null);
  const [caseData, setCaseData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, reset } = useForm<CaseFormValues>({
    defaultValues: { name: "" },
  });

  const handleCreateCase = async (values: CaseFormValues) => {
    setLoading(true);
    setError(null);
    try {
      const data = await createCase(values.name || undefined);
      setCaseId(data.id);
      setCaseData(data);
      reset();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const refreshCase = async () => {
    if (!caseId) return;
    const data = await getCase(caseId);
    setCaseData(data);
  };

  const handleAnalyze = async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      await analyzeCase(caseId);
      await refreshCase();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    try {
      await generateReport(caseId);
      await refreshCase();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen px-6 py-10">
      <div className="mx-auto max-w-5xl space-y-6">
        <header className="space-y-2">
          <h1 className="text-2xl font-semibold">中古マンション管理DD & リノベ制限チェック</h1>
          <p className="text-sm text-slate-600">
            一次資料のみを根拠に、管理DDとリノベ制限の2枚レポを生成します。
          </p>
        </header>

        <section className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
          <h2 className="text-lg font-semibold">案件作成</h2>
          <form
            className="mt-3 flex flex-col gap-3 md:flex-row md:items-center"
            onSubmit={handleSubmit(handleCreateCase)}
          >
            <input
              className="flex-1 rounded border border-slate-300 px-3 py-2"
              placeholder="物件名（任意）"
              {...register("name")}
            />
            <button
              type="submit"
              className="rounded bg-emerald-600 px-4 py-2 text-white disabled:opacity-40"
              disabled={loading}
            >
              {loading ? "作成中..." : "案件を作成"}
            </button>
          </form>
        </section>

        {caseId ? (
          <section className="space-y-4">
            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-lg font-semibold">資料アップロード</h2>
              <p className="text-sm text-slate-500">
                重調・工事・規約・細則・長修をそれぞれ選択してアップロードしてください。
              </p>
              <div className="mt-4">
                <DocumentUploader caseId={caseId} onUploaded={refreshCase} />
              </div>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-lg font-semibold">アップロード状況</h2>
              <div className="mt-3 space-y-2 text-sm">
                {caseData?.documents?.length ? (
                  caseData.documents.map((doc: any) => (
                    <div key={doc.id} className="flex flex-col gap-1 border-b border-dashed border-slate-200 pb-2">
                      <span>種別: {doc.doc_type}</span>
                      <span>ファイル: {doc.filename}</span>
                      <span>ページ数: {doc.page_count ?? "未抽出"}</span>
                    </div>
                  ))
                ) : (
                  <p className="text-slate-500">まだ資料がありません。</p>
                )}
              </div>
            </div>

            <div className="flex flex-col gap-3 md:flex-row">
              <button
                type="button"
                className="flex-1 rounded bg-slate-900 px-4 py-3 text-white disabled:opacity-40"
                onClick={handleAnalyze}
                disabled={loading}
              >
                評価して（解析）
              </button>
              <button
                type="button"
                className="flex-1 rounded bg-indigo-600 px-4 py-3 text-white disabled:opacity-40"
                onClick={handleGenerateReport}
                disabled={loading}
              >
                2枚レポ生成
              </button>
              {caseData?.report_markdown ? (
                <a
                  className="flex-1 rounded border border-slate-300 px-4 py-3 text-center"
                  href={reportPdfUrl(caseId)}
                  target="_blank"
                >
                  PDFダウンロード
                </a>
              ) : null}
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-lg font-semibold">抽出結果</h2>
              <pre className="mt-3 max-h-64 overflow-auto rounded bg-slate-900 p-3 text-xs text-slate-100">
                {caseData?.extracted_metrics
                  ? JSON.stringify(caseData.extracted_metrics, null, 2)
                  : "解析前"}
              </pre>
            </div>

            <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
              <h2 className="text-lg font-semibold">2枚レポ（Markdown）</h2>
              <pre className="mt-3 max-h-96 overflow-auto whitespace-pre-wrap rounded bg-slate-100 p-3 text-sm">
                {caseData?.report_markdown ?? "レポ未生成"}
              </pre>
            </div>
          </section>
        ) : null}

        {error ? <p className="text-sm text-rose-600">{error}</p> : null}
      </div>
    </main>
  );
}
