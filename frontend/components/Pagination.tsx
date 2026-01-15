'use client'

import { useI18n } from '@/lib/i18n'

interface PaginationProps {
    currentPage: number
    totalPages: number
    onPageChange: (page: number) => void
}

export default function Pagination({ currentPage, totalPages, onPageChange }: PaginationProps) {
    const { t } = useI18n()

    // Generate page number array
    const getPageNumbers = () => {
        const pages: (number | 'ellipsis')[] = []

        if (totalPages <= 7) {
            // If total pages <= 7, show all page numbers
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i)
            }
        } else {
            // Always show first page
            pages.push(1)

            if (currentPage <= 3) {
                // Current page is at the beginning
                pages.push(2, 3, 4, 'ellipsis', totalPages)
            } else if (currentPage >= totalPages - 2) {
                // Current page is at the end
                pages.push('ellipsis', totalPages - 3, totalPages - 2, totalPages - 1, totalPages)
            } else {
                // Current page is in the middle
                pages.push('ellipsis', currentPage - 1, currentPage, currentPage + 1, 'ellipsis', totalPages)
            }
        }

        return pages
    }

    const pages = getPageNumbers()

    return (
        <nav className="flex items-center justify-center gap-1" aria-label="Pagination">
            {/* Previous page button */}
            <button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className={`
                    p-2 rounded-lg transition-all duration-200
                    ${currentPage === 1
                        ? 'text-text-muted cursor-not-allowed'
                        : 'text-text-secondary hover:bg-white/60 hover:text-primary-500'
                    }
                `}
                aria-label={t('search.prev_page')}
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
                </svg>
            </button>

            {/* Page number buttons */}
            {pages.map((page, index) => {
                if (page === 'ellipsis') {
                    return (
                        <span key={`ellipsis-${index}`} className="px-2 text-text-muted">
                            ...
                        </span>
                    )
                }

                const isActive = page === currentPage

                return (
                    <button
                        key={page}
                        onClick={() => onPageChange(page)}
                        className={`
                            min-w-[2.5rem] h-10 rounded-lg text-sm font-medium transition-all duration-200
                            ${isActive
                                ? 'bg-primary-500 text-white shadow-minimal-md'
                                : 'text-text-secondary hover:bg-white/60 hover:text-primary-500'
                            }
                        `}
                        aria-current={isActive ? 'page' : undefined}
                    >
                        {page}
                    </button>
                )
            })}

            {/* Next page button */}
            <button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className={`
                    p-2 rounded-lg transition-all duration-200
                    ${currentPage === totalPages
                        ? 'text-text-muted cursor-not-allowed'
                        : 'text-text-secondary hover:bg-white/60 hover:text-primary-500'
                    }
                `}
                aria-label={t('search.next_page')}
            >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
                </svg>
            </button>
        </nav>
    )
}
