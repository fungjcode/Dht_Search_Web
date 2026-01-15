'use client'

import { useEffect, useState } from 'react'
import { useI18n } from '@/lib/i18n'

export default function BackToTop() {
    const { t } = useI18n()
    const [isVisible, setIsVisible] = useState(false)

    useEffect(() => {
        const toggleVisibility = () => {
            if (window.scrollY > 400) {
                setIsVisible(true)
            } else {
                setIsVisible(false)
            }
        }

        window.addEventListener('scroll', toggleVisibility, { passive: true })
        return () => window.removeEventListener('scroll', toggleVisibility)
    }, [])

    const scrollToTop = () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth',
        })
    }

    return (
        <button
            onClick={scrollToTop}
            className={`
                fixed bottom-6 right-6 z-50
                w-12 h-12 rounded-full
                bg-white/80 backdrop-blur-lg
                border border-white/50
                shadow-glass-lg
                flex items-center justify-center
                text-primary-500
                transition-all duration-300 ease-out
                hover:bg-primary-500 hover:text-white
                hover:shadow-minimal-lg hover:-translate-y-1
                ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4 pointer-events-none'}
            `}
            aria-label={t('common.back_to_top')}
            title={t('common.back_to_top')}
        >
            <svg
                className="w-5 h-5"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={2}
            >
                <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 10l7-7m0 0l7 7m-7-7v18"
                />
            </svg>
        </button>
    )
}
