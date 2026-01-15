'use client'

import { useI18n } from '@/lib/i18n'
import siteConfig from '@/config/site'
import Footer from '@/components/Footer'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import BackToTop from '@/components/BackToTop'

export default function AboutContent() {
    const { t } = useI18n()
    const siteName = siteConfig.name

    return (
        <div className="min-h-screen flex flex-col">
            {/* Top navigation - Glassmorphism */}
            <header className="glass sticky top-0 z-10">
                <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
                    <a href="/" className="font-display text-2xl font-bold text-text-primary">
                        {siteConfig.name}
                    </a>
                    <LanguageSwitcher />
                </div>
            </header>

            <div className="flex-1 max-w-4xl mx-auto px-4 py-12 w-full">
                <h1 className="font-display text-4xl font-bold text-text-primary mb-8 animate-fade-in">
                    {t('about.title')}
                </h1>

                <div className="space-y-6">
                    {/* Project overview - Glassmorphism */}
                    <section className="glass rounded-2xl p-8 animate-fade-in">
                        <h2 className="font-display text-2xl font-semibold mb-4">{t('about.overview')}</h2>
                        <p className="text-text-secondary leading-relaxed mb-4">
                            {t('about.overview_text', { siteName })}
                        </p>
                        <p className="text-text-secondary leading-relaxed">
                            {t('about.overview_text2', { siteName })}
                        </p>
                    </section>

                    {/* Usage guide - Claymorphism */}
                    <section className="clay p-8 animate-fade-in">
                        <h2 className="font-display text-2xl font-semibold mb-4">{t('about.usage')}</h2>
                        <p className="text-text-secondary leading-relaxed mb-4">
                            {t('about.usage_text', { siteName })}
                        </p>
                        <p className="text-text-secondary leading-relaxed">
                            {t('about.usage_text2', { siteName })}
                        </p>
                    </section>

                    {/* Disclaimer - Claymorphism with accent */}
                    <section className="clay p-8 bg-accent-50 border-accent-100 animate-fade-in">
                        <h2 className="font-display text-2xl font-semibold mb-4 text-accent-700">{t('about.disclaimer')}</h2>
                        <p className="text-text-secondary leading-relaxed mb-4">
                            {t('about.disclaimer_text', { siteName })}
                        </p>
                        <p className="text-text-secondary leading-relaxed">
                            {t('about.disclaimer_text2', { siteName })}
                        </p>
                    </section>

                    {/* Contact info - Glassmorphism */}
                    <section className="glass rounded-2xl p-8 animate-fade-in">
                        <h2 className="font-display text-2xl font-semibold mb-4">{t('about.contact')}</h2>
                        <div className="space-y-3 text-text-secondary">
                            <p>
                                <span className="font-medium text-text-primary">{t('about.email')}:</span>{' '}
                                <a href={`mailto:${siteConfig.contact.email}`} className="text-primary-500 hover:underline">
                                    {siteConfig.contact.email}
                                </a>
                            </p>
                        </div>
                    </section>
                </div>
            </div>

            <Footer />
            <BackToTop />
        </div>
    )
}
