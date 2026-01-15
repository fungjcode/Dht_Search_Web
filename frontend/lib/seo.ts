import { Metadata } from 'next'
import siteConfig from '@/config/site'

// 类型定义：支持国际化字符串
export type I18nString = string | { zh?: string; en?: string }

interface SEOProps {
    title?: I18nString
    description?: I18nString
    keywords?: string
    image?: string
    url?: string
    type?: string
    locale?: 'zh' | 'en'
}

// 获取国际化字符串
export function getI18nText(text: I18nString | undefined, locale: 'zh' | 'en' = 'en', params?: Record<string, string>): string {
    if (!text) return ''
    let value: string
    if (typeof text === 'string') {
        value = text
    } else {
        value = text[locale] || text.zh || text.en || ''
    }

    // 替换变量占位符
    if (params) {
        Object.keys(params).forEach((key) => {
            value = value.replace(new RegExp(`\\{${key}\\}`, 'g'), params[key])
        })
    }
    return value
}

export function generateSEO({
    title,
    description,
    keywords,
    image,
    url,
    type = 'website',
    locale = 'en',
}: SEOProps = {}): Metadata {
    const siteName = siteConfig.name
    const siteTitle = title
        ? `${getI18nText(title, locale, { siteName })} | ${siteName}`
        : getI18nText(siteConfig.seo.defaultTitle, locale)

    const siteDescription = getI18nText(description || siteConfig.seo.defaultDescription, locale, { siteName })
    const siteKeywords = keywords || siteConfig.keywords
    const siteUrl = url || siteConfig.url
    const siteImage = image || `${siteConfig.url}/og-image.png`

    return {
        title: siteTitle,
        description: siteDescription,
        keywords: siteKeywords,

        // Open Graph
        openGraph: {
            title: siteTitle,
            description: siteDescription,
            url: siteUrl,
            siteName: siteConfig.name,
            images: [{ url: siteImage }],
            locale: locale === 'zh' ? 'zh_CN' : 'en_US',
            type: type as any,
        },

        // Twitter
        twitter: {
            card: 'summary_large_image',
            title: siteTitle,
            description: siteDescription,
            images: [siteImage],
        },

        // Robots
        robots: {
            index: true,
            follow: true,
            googleBot: {
                index: true,
                follow: true,
                'max-video-preview': -1,
                'max-image-preview': 'large',
                'max-snippet': -1,
            },
        },

        // Verification
        verification: {
            google: 'your-google-verification-code',
            // yandex: 'your-yandex-verification-code',
            // bing: 'your-bing-verification-code',
        },
    }
}

// 生成 JSON-LD 结构化数据
export function generateJSONLD(data: any) {
    return {
        __html: JSON.stringify(data),
    }
}

// 网站结构化数据
export function getWebsiteJSONLD(locale: 'zh' | 'en' = 'en') {
    return {
        '@context': 'https://schema.org',
        '@type': 'WebSite',
        name: siteConfig.name,
        description: getI18nText(siteConfig.description, locale),
        url: siteConfig.url,
        potentialAction: {
            '@type': 'SearchAction',
            target: {
                '@type': 'EntryPoint',
                urlTemplate: `${siteConfig.url}/search?q={search_term_string}`,
            },
            'query-input': 'required name=search_term_string',
        },
    }
}

// 种子详情结构化数据
export function torrentJSONLD(torrent: any) {
    return {
        '@context': 'https://schema.org',
        '@type': 'DigitalDocument',
        name: torrent.name,
        description: `${torrent.name} - ${(torrent.total_size / (1024 ** 3)).toFixed(2)} GB`,
        dateCreated: torrent.created_at,
        dateModified: torrent.last_seen,
        fileSize: torrent.total_size,
    }
}
