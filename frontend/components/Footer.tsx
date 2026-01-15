'use client'

import { useI18n } from '@/lib/i18n'
import siteConfig from '@/config/site'

export default function Footer() {
    const { t } = useI18n()
    const currentYear = new Date().getFullYear()

    return (
        <footer className="mt-auto py-8 relative z-10">
            <div className="max-w-6xl mx-auto px-4">
                {/* Glass divider line */}
                <div className="h-px bg-gradient-to-r from-transparent via-white/50 to-transparent mb-6" />

                <div className="flex flex-col md:flex-row items-center justify-between gap-4 text-sm">
                    {/* Left: copyright info */}
                    <div className="flex items-center gap-2 text-text-secondary">
                        <span className="text-text-muted">
                            &copy; {currentYear}
                        </span>
                        <span className="font-medium text-text-primary">
                            {siteConfig.name}
                        </span>
                        <span className="hidden md:inline text-text-muted">•</span>
                        <span className="text-text-muted">
                            {t('footer.rights_reserved')}
                        </span>
                    </div>

                    {/* Right: links */}
                    <div className="flex items-center gap-6">
                        <a
                            href="/about"
                            className="text-text-secondary hover:text-primary-500 transition-colors duration-200"
                        >
                            {t('footer.about')}
                        </a>
                        {siteConfig.features.enableDMCA && (
                            <a
                                href="/dmca"
                                className="text-text-secondary hover:text-primary-500 transition-colors duration-200"
                            >
                                {t('footer.dmca')}
                            </a>
                        )}
                    </div>
                </div>
            </div>
        </footer>
    )
}
