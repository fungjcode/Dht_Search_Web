'use client'

import { useI18n } from '@/lib/i18n'

export default function LanguageSwitcher() {
    const { locale, setLocale, t } = useI18n()

    return (
        <div className="flex items-center gap-1 p-1 glass rounded-xl">
            <button
                onClick={() => setLocale('zh')}
                className={`
                    px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
                    ${locale === 'zh'
                        ? 'bg-primary-500 text-white shadow-minimal-md'
                        : 'text-text-secondary hover:text-text-primary hover:bg-white/50'
                    }
                `}
            >
                {t('locale.zh')}
            </button>
            <button
                onClick={() => setLocale('en')}
                className={`
                    px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200
                    ${locale === 'en'
                        ? 'bg-primary-500 text-white shadow-minimal-md'
                        : 'text-text-secondary hover:text-text-primary hover:bg-white/50'
                    }
                `}
            >
                {t('locale.en')}
            </button>
        </div>
    )
}
