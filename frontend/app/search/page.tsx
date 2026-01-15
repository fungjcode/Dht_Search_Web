'use client'

import { useEffect, useState } from 'react'
import { useSearchParams } from 'next/navigation'
import SearchBox from '@/components/SearchBox'
import { FullPageLoader } from '@/components/LoadingSpinner'
import TorrentCard from '@/components/TorrentCard'
import Pagination from '@/components/Pagination'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import Footer from '@/components/Footer'
import BackToTop from '@/components/BackToTop'
import { useI18n } from '@/lib/i18n'
import siteConfig from '@/config/site'

export default function SearchPage() {
    const searchParams = useSearchParams()
    const { t, locale } = useI18n()
    const keyword = searchParams.get('q') || ''
    const page = parseInt(searchParams.get('page') || '1')
    const sortParam = searchParams.get('sort') || 'time'

    const [results, setResults] = useState<any[]>([])
    const [total, setTotal] = useState(0)
    const [totalPages, setTotalPages] = useState(0)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [sort, setSort] = useState(sortParam)
    const [filters, setFilters] = useState({
        has_video: false,
        has_audio: false,
    })

    // Generate SEO title
    const getPageTitle = () => {
        if (!keyword) return siteConfig.name
        const titleKey = total > 0 ? 'search_results_for' : 'searching_for'
        const titleText = t(`seo.${titleKey}`, { keyword })
        const template = siteConfig.seo.searchTitleTemplate[locale as keyof typeof siteConfig.seo.searchTitleTemplate] || '%s - %s'
        return template.replace('%s', titleText).replace('%s', siteConfig.name)
    }

    // Update page title
    useEffect(() => {
        document.title = getPageTitle()
    }, [keyword, total, locale])

    useEffect(() => {
        if (keyword) {
            fetchResults()
        } else {
            setLoading(false)
        }
    }, [keyword, page, sort, filters])

    const fetchResults = async () => {
        setLoading(true)
        setError(null)
        try {
            const params = new URLSearchParams({
                q: keyword,
                page: page.toString(),
                sort,
                limit: siteConfig.pagination.defaultPageSize.toString(),
            })

            if (filters.has_video) params.append('has_video', 'true')
            if (filters.has_audio) params.append('has_audio', 'true')

            const apiKey = process.env.NEXT_PUBLIC_API_KEY || 'demo_key_12345'
            params.append('api_key', apiKey)

            const res = await fetch(`${siteConfig.apiUrl}/api/search?${params}`)

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}))
                const detail = errData.detail?.message || errData.detail || `HTTP ${res.status}`
                throw new Error(detail)
            }

            const data = await res.json()
            setResults(data.results || [])
            setTotal(data.total || 0)
            setTotalPages(data.total_pages || 0)
        } catch (err: any) {
            console.error('Search error:', err)
            setError(err.message || t('common.error'))
            setResults([])
            setTotal(0)
        } finally {
            setLoading(false)
        }
    }

    const handleSearch = (newKeyword: string) => {
        window.location.href = `/search?q=${encodeURIComponent(newKeyword)}`
    }

    const handleSortChange = (newSort: string) => {
        setSort(newSort)
        const params = new URLSearchParams(window.location.search)
        params.set('sort', newSort)
        window.history.pushState({}, '', `?${params}`)
    }

    const handlePageChange = (newPage: number) => {
        const params = new URLSearchParams(window.location.search)
        params.set('page', newPage.toString())
        window.location.href = `?${params}`
    }

    return (
        <div className="min-h-screen flex flex-col">
            {/* Top navigation - Glassmorphism */}
            <header className="glass sticky top-0 z-10 flex-shrink-0">
                <div className="max-w-6xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between gap-4">
                        <a href="/" className="font-display text-2xl font-bold text-text-primary whitespace-nowrap hidden md:block">
                            {siteConfig.name}
                        </a>
                        <div className="flex-1 max-w-2xl mx-auto md:mx-0 hidden md:block">
                            <SearchBox
                                onSearch={handleSearch}
                                initialValue={keyword}
                            />
                        </div>
                        <div className="flex items-center gap-3">
                            <a href="/" className="md:hidden font-display text-lg font-bold text-text-primary whitespace-nowrap mr-2">
                                {siteConfig.name}
                            </a>
                            <LanguageSwitcher />
                        </div>
                    </div>
                </div>
            </header>

            <div className="flex-1 max-w-6xl mx-auto px-4 py-8 w-full">
                {/* Search results count */}
                <div className="mb-6 text-text-secondary animate-fade-in">
                    {t('search.results_count', { count: total.toLocaleString() })}
                </div>

                {/* Sort and filter - Glassmorphism */}
                <div className="glass rounded-xl p-4 mb-6 flex flex-wrap gap-y-3 items-center animate-fade-in">
                    {/* Sort */}
                    <div className="flex items-center gap-2 flex-nowrap flex-shrink-0">
                        <span className="text-sm text-text-secondary whitespace-nowrap">{t('search.sort_by')}:</span>
                        <select
                            value={sort}
                            onChange={(e) => handleSortChange(e.target.value)}
                            className="input-minimal py-2 px-3 text-sm w-32 flex-shrink-0"
                        >
                            {siteConfig.search.sortOptions.map((option) => {
                                const label = typeof option.label === 'object'
                                    ? (option.label[locale] || option.label.zh || option.value)
                                    : t(`search.sort_options.${option.value}`)
                                return (
                                    <option key={option.value} value={option.value}>
                                        {label}
                                    </option>
                                )
                            })}
                        </select>
                    </div>

                    {/* Filter */}
                    <div className="flex items-center gap-4 ml-auto">
                        <label className="flex items-center gap-2 text-sm cursor-pointer whitespace-nowrap">
                            <input
                                type="checkbox"
                                checked={filters.has_video}
                                onChange={(e) => setFilters({ ...filters, has_video: e.target.checked })}
                                className="w-4 h-4 rounded border-border-light text-primary-500 focus:ring-primary-500/20"
                            />
                            <span className="text-text-secondary">{t('search.filters.video')}</span>
                        </label>
                        <label className="flex items-center gap-2 text-sm cursor-pointer whitespace-nowrap">
                            <input
                                type="checkbox"
                                checked={filters.has_audio}
                                onChange={(e) => setFilters({ ...filters, has_audio: e.target.checked })}
                                className="w-4 h-4 rounded border-border-light text-primary-500 focus:ring-primary-500/20"
                            />
                            <span className="text-text-secondary">{t('search.filters.audio')}</span>
                        </label>
                    </div>
                </div>

                {/* Search results list */}
                {loading ? (
                    <FullPageLoader text={t('common.loading')} />
                ) : error ? (
                    <div className="text-center py-12 glass rounded-xl animate-fade-in">
                        <div className="text-4xl mb-4">⚠️</div>
                        <p className="text-text-primary text-lg mb-2">{error}</p>
                        <p className="text-text-muted text-sm">{t('common.check_network')}</p>
                    </div>
                ) : results.length > 0 ? (
                    <>
                        <div className="space-y-4 mb-8">
                            {results.map((torrent) => (
                                <TorrentCard
                                    key={torrent.info_hash}
                                    torrent={torrent}
                                    searchKeyword={keyword}
                                />
                            ))}
                        </div>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="py-6 animate-fade-in">
                                <Pagination
                                    currentPage={page}
                                    totalPages={totalPages}
                                    onPageChange={handlePageChange}
                                />
                            </div>
                        )}
                    </>
                ) : (
                    <div className="text-center py-12 animate-fade-in">
                        <div className="text-5xl mb-4">🔍</div>
                        <p className="text-text-primary text-lg mb-2">{t('search.no_results')}</p>
                        <p className="text-text-muted text-sm">{t('search.try_other')}</p>
                    </div>
                )}
            </div>

            <Footer />
            <BackToTop />
        </div>
    )
}
