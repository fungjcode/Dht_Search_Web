import type { Metadata } from 'next'
import { generateSEO } from '@/lib/seo'
import AboutContent from './AboutContent'

export const metadata: Metadata = generateSEO({
    title: { zh: '关于我们', en: 'About Us' },
    description: {
        zh: '{siteName} 是一个开源的 DHT 种子搜索引擎项目',
        en: '{siteName} is an open source DHT torrent search engine project',
    },
})

export default function AboutPage() {
    return <AboutContent />
}
