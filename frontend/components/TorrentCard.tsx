'use client'

import { useI18n } from '@/lib/i18n'
import { showToast } from '@/components/Toast'

interface TorrentCardProps {
    torrent: {
        info_hash: string
        name: string
        total_size: number
        file_count: number
        health_score: number
        has_video?: boolean
        has_audio?: boolean
        created_at: string
    }
    searchKeyword?: string
}

export default function TorrentCard({ torrent, searchKeyword }: TorrentCardProps) {
    const { t } = useI18n()

    const formatSize = (bytes: number) => {
        const gb = bytes / (1024 ** 3)
        return gb >= 1 ? `${gb.toFixed(2)} GB` : `${(bytes / (1024 ** 2)).toFixed(2)} MB`
    }

    const dateT = (key: string, params?: Record<string, string>) => t(`common.date.${key}`, params)

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr)
        const now = new Date()
        const diffDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24))

        if (diffDays === 0) return dateT('today')
        if (diffDays === 1) return dateT('yesterday')
        if (diffDays < 7) return dateT('days_ago', { count: diffDays.toString() })
        if (diffDays < 30) return dateT('weeks_ago', { count: Math.floor(diffDays / 7).toString() })
        if (diffDays < 365) return dateT('months_ago', { count: Math.floor(diffDays / 30).toString() })
        return dateT('years_ago', { count: Math.floor(diffDays / 365).toString() })
    }

    const getHealthColor = (score: number) => {
        if (score >= 70) return 'text-green-500'
        if (score >= 40) return 'text-yellow-500'
        return 'text-red-500'
    }

    // Build detail page URL with search keyword param
    const getDetailUrl = () => {
        const url = `/torrent/${torrent.info_hash}`
        if (searchKeyword) {
            return `${url}?from=${encodeURIComponent(searchKeyword)}`
        }
        return url
    }

    const handleCopy = (e: React.MouseEvent) => {
        e.preventDefault()
        navigator.clipboard.writeText(`magnet:?xt=urn:btih:${torrent.info_hash}`)
        showToast(t('torrent.copy_success'), 'success')
    }

    return (
        <a
            href={getDetailUrl()}
            className="minimal-hover block p-5 group"
        >
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                {/* Left: title and tags */}
                <div className="flex-1 min-w-0">
                    <h3 className="text-base md:text-lg font-medium text-text-primary mb-2.5 truncate group-hover:text-primary-600 transition-colors">
                        {torrent.name}
                    </h3>
                    <div className="flex flex-wrap items-center gap-2.5 text-sm text-text-secondary">
                        <span className="font-medium">{formatSize(Number(torrent.total_size || 0))}</span>
                        <span className="text-text-muted">•</span>
                        <span>{torrent.file_count} {t('torrent.files')}</span>
                        <span className="text-text-muted">•</span>
                        <span className={getHealthColor(Number(torrent.health_score || 0))}>
                            {t('torrent.health')}: {Number(torrent.health_score || 0) > 0 ? Number(torrent.health_score).toFixed(0) : '-'}
                        </span>
                        <span className="text-text-muted">•</span>
                        <span className="text-text-muted">{formatDate(torrent.created_at)}</span>
                    </div>
                </div>

                {/* Right: action buttons */}
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleCopy}
                        className="btn-secondary text-sm py-2 px-4"
                    >
                        <svg className="w-4 h-4 mr-1.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        {t('common.copy')}
                    </button>
                </div>
            </div>
        </a>
    )
}
