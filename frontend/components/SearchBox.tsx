'use client'

import { useState, KeyboardEvent } from 'react'
import { useI18n } from '@/lib/i18n'
import { showToast } from '@/components/Toast'

interface SearchBoxProps {
    onSearch: (keyword: string) => void
    initialValue?: string
    autoFocus?: boolean
    placeholder?: string
}

export default function SearchBox({
    onSearch,
    initialValue = '',
    autoFocus = false,
}: SearchBoxProps) {
    const { t } = useI18n()
    const [keyword, setKeyword] = useState(initialValue)

    const handleSearch = () => {
        const trimmedKeyword = keyword.trim()
        if (!trimmedKeyword) {
            showToast(t('search.empty_keyword'), 'warning')
            return
        }
        onSearch(trimmedKeyword)
    }

    const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter') {
            handleSearch()
        }
    }

    return (
        <div className="flex gap-2 w-full">
            <div className="relative flex-1">
                <input
                    type="text"
                    value={keyword}
                    onChange={(e) => setKeyword(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={t('common.search_placeholder')}
                    autoFocus={autoFocus}
                    className="input-glass pl-4 pr-11 py-3 w-full"
                />
                {/* Search icon - positioned on the right */}
                <svg
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-text-muted pointer-events-none"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    strokeWidth={2}
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                    />
                </svg>
            </div>
            <button
                onClick={handleSearch}
                className="btn-primary hidden md:flex items-center gap-2"
            >
                <span>{t('common.search')}</span>
            </button>
        </div>
    )
}
