import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Runpod Text Models - Post Generator',
  description: 'Generate social media posts using AI models',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

