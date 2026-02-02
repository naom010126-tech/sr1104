"use client";

import { useState } from "react";
import { uploadDocument } from "../lib/api";

const DOC_TYPES = ["重調", "工事", "規約", "細則", "長修"] as const;

type Props = {
  caseId: number;
  onUploaded: () => void;
};

export default function DocumentUploader({ caseId, onUploaded }: Props) {
  const [selectedType, setSelectedType] = useState<string>("重調");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async () => {
    if (!file) {
      setError("ファイルを選択してください");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await uploadDocument(caseId, selectedType, file);
      setFile(null);
      onUploaded();
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex flex-col gap-2 md:flex-row md:items-center">
        <select
          className="rounded border border-slate-300 px-3 py-2"
          value={selectedType}
          onChange={(event) => setSelectedType(event.target.value)}
        >
          {DOC_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
        <input
          type="file"
          accept="application/pdf"
          onChange={(event) => setFile(event.target.files?.[0] || null)}
        />
        <button
          type="button"
          className="rounded bg-slate-900 px-4 py-2 text-white disabled:opacity-40"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? "アップロード中..." : "アップロード"}
        </button>
      </div>
      {error ? <p className="text-sm text-rose-600">{error}</p> : null}
    </div>
  );
}
