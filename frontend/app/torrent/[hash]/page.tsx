'use client'

import { useEffect, useState } from 'react'
import { useParams, useRouter, useSearchParams } from 'next/navigation'
import { FullPageLoader } from '@/components/LoadingSpinner'
import SearchBox from '@/components/SearchBox'
import Footer from '@/components/Footer'
import siteConfig from '@/config/site'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import BackToTop from '@/components/BackToTop'
import { useI18n } from '@/lib/i18n'
import { showToast } from '@/components/Toast'

interface Torrent {
    id: string
    info_hash: string
    name: string
    total_size: number
    file_count: number
    health_score: number
    created_at: string
    last_seen: string
}

interface TorrentFile {
    file_name: string
    file_path: string
    file_size: number
    file_extension: string
}

export default function TorrentDetail() {
    const params = useParams()
    const router = useRouter()
    const searchParams = useSearchParams()
    const { t, locale } = useI18n()
    const info_hash = params.hash as string
    const searchKeyword = searchParams.get('from') || ''

    const [torrent, setTorrent] = useState<Torrent | null>(null)
    const [files, setFiles] = useState<TorrentFile[]>([])
    const [recommendations, setRecommendations] = useState<Torrent[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    // Generate SEO title
    const getPageTitle = () => {
        if (!torrent) return siteConfig.name
        const torrentName = torrent.name.length > 50
            ? torrent.name.substring(0, 50) + '...'
            : torrent.name
        const template = siteConfig.seo.detailTitleTemplate[locale as keyof typeof siteConfig.seo.detailTitleTemplate] || '%s - %s'
        return template.replace('%s', torrentName).replace('%s', siteConfig.name)
    }

    // Update page title
    useEffect(() => {
        document.title = getPageTitle()
    }, [torrent, locale])

    useEffect(() => {
        if (info_hash) {
            fetchTorrentDetail()
            fetchRecommendations()
        }
    }, [info_hash])

    const fetchTorrentDetail = async () => {
        try {
            const res = await fetch(`${siteConfig.apiUrl}/api/torrent/${info_hash}`)
            if (!res.ok) throw new Error(t('search.no_results'))

            const data = await res.json()
            setTorrent(data.torrent)
            setFiles(data.files)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const fetchRecommendations = async () => {
        try {
            if (searchKeyword) {
                const params = new URLSearchParams({
                    q: searchKeyword,
                    limit: '5',
                    sort: 'health',
                })
                const res = await fetch(`${siteConfig.apiUrl}/api/search?${params}`)
                if (res.ok) {
                    const data = await res.json()
                    const otherResults = (data.results || []).filter(
                        (t: any) => t.info_hash !== info_hash
                    )
                    setRecommendations(otherResults.slice(0, 5))
                }
            }
        } catch (err) {
            console.error('Failed to fetch recommendations:', err)
        }
    }

    const formatSize = (bytes: number) => {
        const gb = bytes / (1024 ** 3)
        return gb >= 1 ? `${gb.toFixed(2)} GB` : `${(bytes / (1024 ** 2)).toFixed(2)} MB`
    }

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString()
    }

    const copyMagnetLink = () => {
        const magnetLink = `magnet:?xt=urn:btih:${info_hash}`
        navigator.clipboard.writeText(magnetLink)
        showToast(t('torrent.copy_success'), 'success')
    }

    const handleSearch = (newKeyword: string) => {
        router.push(`/search?q=${encodeURIComponent(newKeyword)}`)
    }

    if (loading) {
        return <FullPageLoader text={t('common.loading')} />
    }

    if (error || !torrent) {
        return (
            <div className="min-h-screen flex flex-col items-center justify-center">
                <div className="text-center glass rounded-2xl p-8 max-w-md">
                    <div className="text-5xl mb-4">⚠️</div>
                    <h2 className="font-display text-2xl font-bold text-text-primary mb-4">
                        {t('common.error')}
                    </h2>
                    <p className="text-text-secondary mb-6">{error || t('search.no_results')}</p>
                    <a href="/" className="btn-primary inline-block">
                        {t('common.go_search')}
                    </a>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen flex flex-col">
            {/* Top navigation - Glassmorphism */}
            <header className="glass sticky top-0 z-10">
                <div className="max-w-6xl mx-auto px-4 py-4">
                    <div className="flex items-center justify-between gap-4">
                        <a href="/" className="font-display text-2xl font-bold text-text-primary whitespace-nowrap hidden md:block">
                            {siteConfig.name}
                        </a>
                        <div className="flex-1 max-w-2xl mx-auto md:mx-0 hidden md:block">
                            <SearchBox
                                onSearch={handleSearch}
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
                {/* Torrent title */}
                <h1 className="font-display text-2xl md:text-3xl font-bold text-text-primary mb-6 break-all animate-fade-in">
                    {torrent.name}
                </h1>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left main content */}
                    <div className="lg:col-span-2 space-y-6">
                        {/* Basic info - Glassmorphism */}
                        <div className="glass rounded-2xl p-6 animate-fade-in">
                            <h2 className="font-display text-xl font-semibold mb-4">{t('torrent.basic_info')}</h2>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                                <div>
                                    <span className="text-text-muted">{t('torrent.size')}:</span>
                                    <span className="ml-2 font-medium text-text-primary">{formatSize(torrent.total_size)}</span>
                                </div>
                                <div>
                                    <span className="text-text-muted">{t('torrent.files_count')}:</span>
                                    <span className="ml-2 font-medium text-text-primary">{torrent.file_count}</span>
                                </div>
                                <div>
                                    <span className="text-text-muted">{t('torrent.health')}:</span>
                                    <span className={`ml-2 font-medium ${torrent.health_score > 50 ? 'text-green-500' : 'text-yellow-500'}`}>
                                        {torrent.health_score > 0 ? torrent.health_score : '-'}
                                    </span>
                                </div>
                                <div>
                                    <span className="text-text-muted">{t('torrent.created_at')}:</span>
                                    <span className="ml-2 font-medium text-text-primary">{formatDate(torrent.created_at)}</span>
                                </div>
                                <div>
                                    <span className="text-text-muted">{t('torrent.last_seen')}:</span>
                                    <span className="ml-2 font-medium text-text-primary">{formatDate(torrent.last_seen)}</span>
                                </div>
                                <div className="col-span-2">
                                    <span className="text-text-muted">{t('torrent.hash')}:</span>
                                    <span className="ml-2 font-mono text-xs text-text-secondary break-all">{info_hash}</span>
                                </div>
                            </div>
                        </div>

                        {/* Magnet link - Glassmorphism */}
                        <div className="glass rounded-2xl p-6 animate-fade-in">
                            <h2 className="font-display text-xl font-semibold mb-4">{t('torrent.magnet_link')}</h2>
                            <div className="flex flex-col sm:flex-row gap-2">
                                <input
                                    type="text"
                                    value={`magnet:?xt=urn:btih:${info_hash}`}
                                    readOnly
                                    className="input-glass flex-1 font-mono text-sm"
                                />
                                <button onClick={copyMagnetLink} className="btn-primary whitespace-nowrap">
                                    <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                                        <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                    </svg>
                                    {t('common.copy')}
                                </button>
                            </div>
                        </div>

                        {/* File list - Glassmorphism */}
                        {files.length > 0 ? (
                            <div className="glass rounded-2xl p-6 animate-fade-in">
                                <h2 className="font-display text-xl font-semibold mb-4">{t('torrent.file_list')}</h2>
                                <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                                    {files.map((file, index) => (
                                        <div key={index} className="flex justify-between items-center py-2.5 border-b border-slate-100 last:border-0 hover:bg-slate-50/50 px-2 rounded-lg transition-colors">
                                            <div className="flex-1 truncate mr-4">
                                                <span className="text-text-muted mr-2 w-6 inline-block text-right">{index + 1}.</span>
                                                <span className="text-sm text-text-primary" title={file.file_name}>{file.file_name}</span>
                                            </div>
                                            <span className="text-xs text-text-muted whitespace-nowrap font-mono">
                                                {formatSize(file.file_size)}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : Number(torrent?.file_count) > 0 ? (
                            <div className="glass rounded-2xl p-6 animate-fade-in">
                                <h2 className="font-display text-xl font-semibold mb-4">{t('torrent.file_list')}</h2>
                                <p className="text-text-muted text-sm">{t('search.no_results')}</p>
                            </div>
                        ) : null}
                    </div>

                    {/* Right sidebar - Claymorphism */}
                    <div className="space-y-6">
                        {/* Recommendations */}
                        {recommendations.length > 0 && (
                            <div className="clay p-6 animate-fade-in">
                                <h2 className="font-display text-xl font-semibold mb-4">{t('torrent.recommendations')}</h2>
                                <div className="space-y-3">
                                    {recommendations.slice(0, 5).map((rec) => {
                                        const recUrl = searchKeyword
                                            ? `/torrent/${rec.info_hash}?from=${encodeURIComponent(searchKeyword)}`
                                            : `/torrent/${rec.info_hash}`
                                        return (
                                            <a
                                                key={rec.info_hash}
                                                href={recUrl}
                                                className="block p-3 bg-slate-50 rounded-xl hover:bg-slate-100 transition-colors border border-slate-100"
                                            >
                                                <h3 className="text-sm font-medium text-text-primary mb-1.5 truncate">
                                                    {rec.name}
                                                </h3>
                                                <div className="flex justify-between text-xs text-text-muted">
                                                    <span>{formatSize(Number(rec.total_size))}</span>
                                                    <span className={Number(rec.health_score) > 50 ? 'text-green-500' : 'text-yellow-500'}>
                                                        ♥ {Number(rec.health_score) > 0 ? rec.health_score : '-'}
                                                    </span>
                                                </div>
                                            </a>
                                        )
                                    })}
                                </div>
                            </div>
                        )}

                        {/* DMCA complaint - Claymorphism with accent */}
                        <div className="clay p-6 border-l-4 border-accent-400 animate-fade-in">
                            <h2 className="font-display text-xl font-semibold mb-3 text-accent-600">{t('torrent.dmca_title')}</h2>
                            <p className="text-sm text-text-secondary mb-4">
                                {t('torrent.dmca_text')}
                            </p>
                            <a href={`/dmca?hash=${info_hash}`} className="btn-primary w-full text-center block bg-accent-500 hover:bg-accent-600">
                                {t('torrent.dmca_button')}
                            </a>
                        </div>
                    </div>
                </div>
            </div>

            <Footer />
            <BackToTop />
        </div>
    )
}
