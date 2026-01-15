'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import SearchBox from '@/components/SearchBox'
import { FullPageLoader } from '@/components/LoadingSpinner'
import Footer from '@/components/Footer'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import { useI18n } from '@/lib/i18n'

export default function Home() {
    const router = useRouter()
    const { t } = useI18n()
    const [loading, setLoading] = useState(false)

    const handleSearch = (keyword: string) => {
        if (!keyword.trim()) return
        setLoading(true)
        router.push(`/search?q=${encodeURIComponent(keyword)}`)
    }

    const hotTags = [
        t('home.hot_tags.movies'),
        t('home.hot_tags.music'),
        t('home.hot_tags.software'),
        t('home.hot_tags.games'),
        t('home.hot_tags.anime'),
    ]

    return (
        <div className="min-h-screen flex flex-col relative overflow-hidden">
            {/* Background decoration - gradient circles */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-200/30 rounded-full blur-3xl animate-float"></div>
                <div className="absolute top-1/2 -left-40 w-96 h-96 bg-accent-200/20 rounded-full blur-3xl animate-float-delayed"></div>
                <div className="absolute -bottom-40 right-1/3 w-72 h-72 bg-primary-300/20 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
            </div>

            {/* Main content area */}
            <div className="flex-1 flex flex-col items-center justify-center px-4 relative z-10">
                {/* Language switcher */}
                <div className="absolute top-6 right-6 z-20">
                    <LanguageSwitcher />
                </div>

                {/* Logo and title */}
                <div className="mb-8 text-center animate-slide-up">
                    <h1 className="font-display text-4xl md:text-6xl font-bold text-text-primary mb-3 tracking-tight">
                        {t('home.title')}
                    </h1>
                    <p className="text-text-secondary text-base md:text-lg">
                        {t('home.subtitle')}
                    </p>
                </div>

                {/* Search box - Glassmorphism */}
                <div className="w-full max-w-2xl mb-8 animate-slide-up" style={{ animationDelay: '0.1s' }}>
                    <SearchBox
                        onSearch={handleSearch}
                        autoFocus
                    />
                </div>

                {/* Hot tags - Claymorphism */}
                <div className="flex flex-wrap gap-2.5 justify-center max-w-lg px-2 animate-slide-up" style={{ animationDelay: '0.2s' }}>
                    {hotTags.map((tag, index) => (
                        <button
                            key={tag}
                            onClick={() => handleSearch(tag)}
                            className="tag-glass"
                            style={{ animationDelay: `${0.3 + index * 0.05}s` }}
                        >
                            {tag}
                        </button>
                    ))}
                </div>
            </div>

            <Footer />

            {/* Full page loading */}
            {loading && (
                <FullPageLoader text={t('common.loading')} />
            )}
        </div>
    )
}
