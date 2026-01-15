import './globals.css'
import type { Metadata } from 'next'
import { I18nProvider } from '@/lib/i18n'
import { siteConfig } from '@/config/site'
import { getI18nText } from '@/lib/seo'

// Helper function to get internationalized text
const getDesc = (locale: 'zh' | 'en' = 'en') => getI18nText(siteConfig.description, locale)

export const metadata: Metadata = {
    metadataBase: new URL(siteConfig.url),
    title: {
        default: siteConfig.name,
        template: `%s | ${siteConfig.name}`,
    },
    description: getDesc('en'),
    keywords: siteConfig.keywords,
    authors: [
        {
            name: siteConfig.name,
            url: siteConfig.url,
        },
    ],
    creator: siteConfig.name,
    openGraph: {
        type: 'website',
        locale: 'en_US',
        url: siteConfig.url,
        siteName: siteConfig.name,
        title: siteConfig.name,
        description: getDesc('en'),
    },
    twitter: {
        card: 'summary_large_image',
        title: siteConfig.name,
        description: getDesc('en'),
    },
    icons: {
        icon: '/favicon.svg',
        shortcut: '/favicon.svg',
    },
}

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" suppressHydrationWarning>
            <body className="font-sans antialiased">
                <I18nProvider>
                    {children}
                </I18nProvider>
            </body>
        </html>
    )
}

