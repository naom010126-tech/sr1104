import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "中古マンション管理DD",
  description: "管理DDとリノベ制限チェックの自動レポ生成",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
