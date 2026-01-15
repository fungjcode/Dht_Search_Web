'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import enTranslations from '@/locales/en.json'
import zhTranslations from '@/locales/zh.json'
import { ToastProvider, setGlobalToast } from '@/components/Toast'

type Locale = 'zh' | 'en'

interface I18nContextType {
    locale: Locale
    setLocale: (locale: Locale) => void
    t: (key: string, params?: Record<string, any>) => string
}

const I18nContext = createContext<I18nContextType | undefined>(undefined)

const translationsMap: Record<Locale, any> = {
    en: enTranslations,
    zh: zhTranslations,
}

export function I18nProvider({ children }: { children: ReactNode }) {
    const [locale, setLocaleState] = useState<Locale>('en')
    const [translations, setTranslations] = useState<any>(enTranslations)
    const [mounted, setMounted] = useState(false)

    useEffect(() => {
        setMounted(true)
        const savedLocale = localStorage.getItem('locale') as Locale
        if (savedLocale && (savedLocale === 'zh' || savedLocale === 'en')) {
            setLocaleState(savedLocale)
            setTranslations(translationsMap[savedLocale])
        }
    }, [])

    const setLocale = (newLocale: Locale) => {
        setLocaleState(newLocale)
        setTranslations(translationsMap[newLocale])
        localStorage.setItem('locale', newLocale)
    }

    const t = (key: string, params?: Record<string, any>) => {
        const keys = key.split('.')
        let value: any = translations

        for (const k of keys) {
            value = value?.[k]
            if (value === undefined) break
        }

        if (typeof value !== 'string') {
            return key
        }

        if (params) {
            Object.keys(params).forEach((param) => {
                // Support both double {{param}} and single {param} curly brace formats
                value = value.replace(new RegExp(`\\{\\{${param}\\}\\}`, 'g'), params[param])
                value = value.replace(new RegExp(`\\{${param}\\}`, 'g'), params[param])
            })
        }

        return value
    }

    // Toast provider wrapper
    const handleShowToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
        // Dispatch custom event for Toast component
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('show-toast', { detail: { message, type } }))
        }
    }

    // Set global toast (for non-React context)
    useEffect(() => {
        setGlobalToast(handleShowToast)
    }, [])

    if (!mounted) {
        return (
            <I18nContext.Provider value={{ locale, setLocale, t }}>
                <div style={{ visibility: 'hidden' }}>{children}</div>
            </I18nContext.Provider>
        )
    }

    return (
        <I18nContext.Provider value={{ locale, setLocale, t }}>
            <ToastProvider>
                {children}
            </ToastProvider>
        </I18nContext.Provider>
    )
}

export function useI18n() {
    const context = useContext(I18nContext)
    if (!context) {
        throw new Error('useI18n must be used within I18nProvider')
    }
    return context
}
