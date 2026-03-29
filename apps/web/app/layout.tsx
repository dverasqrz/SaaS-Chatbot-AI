import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'SaaS Chatbot AI',
  description: 'Chatbot SaaS com Next.js, AI SDK, múltiplos providers e FastAPI',
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
