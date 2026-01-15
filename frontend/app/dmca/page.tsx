'use client'

import { useState, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import siteConfig from '@/config/site'
import LoadingSpinner from '@/components/LoadingSpinner'
import Footer from '@/components/Footer'
import LanguageSwitcher from '@/components/LanguageSwitcher'
import BackToTop from '@/components/BackToTop'
import { useI18n } from '@/lib/i18n'
import zhTranslations from '@/locales/zh.json'
import enTranslations from '@/locales/en.json'

// Get complaint notice items
const getNoticeItems = (locale: string): string[] => {
    const translations = locale === 'zh' ? zhTranslations : enTranslations
    return translations.dmca.notice_items
}

function DMCAContent() {
    const { t, locale } = useI18n()
    const searchParams = useSearchParams()
    const defaultHash = searchParams.get('hash') || ''
    const noticeItems = getNoticeItems(locale)

    const [formData, setFormData] = useState({
        info_hash: defaultHash,
        complainant_name: '',
        complainant_email: '',
        complainant_company: '',
        complaint_reason: '',
        copyright_proof: '',
    })

    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [error, setError] = useState('')

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setSubmitting(true)
        setError('')

        try {
            const res = await fetch(`${siteConfig.apiUrl}/api/dmca`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            })

            if (!res.ok) {
                try {
                    const errData = await res.json()
                    throw new Error(errData.detail || t('common.error'))
                } catch {
                    throw new Error(`${t('common.error')} (HTTP ${res.status})`)
                }
            }

            setSubmitted(true)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setSubmitting(false)
        }
    }

    if (submitted) {
        return (
            <div className="min-h-screen flex items-center justify-center px-4">
                <div className="glass rounded-2xl p-8 max-w-md text-center animate-fade-in">
                    <div className="w-16 h-16 mx-auto mb-4 bg-green-100 rounded-full flex items-center justify-center">
                        <svg className="w-8 h-8 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                        </svg>
                    </div>
                    <h2 className="font-display text-2xl font-bold text-text-primary mb-3">
                        {t('dmca.success')}
                    </h2>
                    <p className="text-text-secondary mb-6">
                        {t('dmca.success_message')}
                    </p>
                    <a href="/" className="btn-primary inline-block">
                        {t('common.back_home')}
                    </a>
                </div>
            </div>
        )
    }

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
                {/* Page title */}
                <h1 className="font-display text-4xl font-bold text-text-primary mb-8 animate-fade-in">
                    {t('dmca.title')}
                </h1>

                {/* Notice - Claymorphism */}
                <div className="clay p-6 mb-8 bg-primary-50/50 border-primary-100 animate-fade-in">
                    <h2 className="font-display text-xl font-semibold mb-4 text-primary-700">
                        {t('dmca.notice')}
                    </h2>
                    <ul className="list-disc list-inside text-text-secondary space-y-2 text-sm">
                        {noticeItems.map((item: string, index: number) => (
                            <li key={index}>{item}</li>
                        ))}
                    </ul>
                </div>

                {/* Complaint form - Glassmorphism */}
                <form onSubmit={handleSubmit} className="glass rounded-2xl p-8 space-y-6 animate-fade-in">
                    {/* Info Hash */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.hash')} <span className="text-accent-500">*</span>
                        </label>
                        <input
                            type="text"
                            required
                            value={formData.info_hash}
                            onChange={(e) => setFormData({ ...formData, info_hash: e.target.value })}
                            placeholder="40-character hexadecimal hash"
                            className="input-glass"
                            pattern="[a-fA-F0-9]{40}"
                        />
                    </div>

                    {/* Complainant name */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.name')} <span className="text-accent-500">*</span>
                        </label>
                        <input
                            type="text"
                            required
                            value={formData.complainant_name}
                            onChange={(e) => setFormData({ ...formData, complainant_name: e.target.value })}
                            className="input-glass"
                        />
                    </div>

                    {/* Email */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.email')} <span className="text-accent-500">*</span>
                        </label>
                        <input
                            type="email"
                            required
                            value={formData.complainant_email}
                            onChange={(e) => setFormData({ ...formData, complainant_email: e.target.value })}
                            className="input-glass"
                        />
                    </div>

                    {/* Company/Organization */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.company')}
                        </label>
                        <input
                            type="text"
                            value={formData.complainant_company}
                            onChange={(e) => setFormData({ ...formData, complainant_company: e.target.value })}
                            className="input-glass"
                        />
                    </div>

                    {/* Complaint reason */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.reason')} <span className="text-accent-500">*</span>
                        </label>
                        <textarea
                            required
                            value={formData.complaint_reason}
                            onChange={(e) => setFormData({ ...formData, complaint_reason: e.target.value })}
                            rows={6}
                            placeholder={t('dmca.form.reason_placeholder')}
                            className="input-glass resize-none"
                        />
                    </div>

                    {/* Copyright proof */}
                    <div>
                        <label className="block text-sm font-medium text-text-primary mb-2">
                            {t('dmca.form.proof')}
                        </label>
                        <input
                            type="url"
                            value={formData.copyright_proof}
                            onChange={(e) => setFormData({ ...formData, copyright_proof: e.target.value })}
                            placeholder="https://..."
                            className="input-glass"
                        />
                        <p className="text-sm text-text-muted mt-2">
                            {t('dmca.form.proof_hint')}
                        </p>
                    </div>

                    {/* Error message */}
                    {error && (
                        <div className="p-4 bg-accent-50 border border-accent-200 rounded-xl text-accent-600">
                            {error}
                        </div>
                    )}

                    {/* Submit button */}
                    <div className="flex gap-4 pt-4">
                        <button
                            type="submit"
                            disabled={submitting}
                            className="btn-primary disabled:opacity-50"
                        >
                            {submitting ? t('dmca.submitting') : t('common.submit')}
                        </button>
                        <a href="/" className="btn-secondary">
                            {t('common.cancel')}
                        </a>
                    </div>
                </form>
            </div>

            <Footer />
            <BackToTop />
        </div>
    )
}

export default function DMCAPage() {
    return (
        <Suspense fallback={
            <div className="min-h-screen flex items-center justify-center">
                <LoadingSpinner />
            </div>
        }>
            <DMCAContent />
        </Suspense>
    )
}
