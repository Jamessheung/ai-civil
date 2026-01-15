import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'AI Civilization News',
    description: 'An observation station for AI civilization events.',
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en">
            <body className="min-h-screen bg-civ-dark text-white">{children}</body>
        </html>
    )
}
