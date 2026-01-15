'use client'

import { createContext, useContext, useState, useCallback, ReactNode, useEffect } from 'react'

interface Toast {
    id: number
    message: string
    type: 'success' | 'error' | 'info' | 'warning'
}

interface ToastContextType {
    showToast: (message: string, type?: Toast['type']) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

let toastId = 0

export function ToastProvider({ children }: { children: ReactNode }) {
    const [toasts, setToasts] = useState<Toast[]>([])

    const showToast = useCallback((message: string, type: Toast['type'] = 'info') => {
        const id = ++toastId
        setToasts((prev) => [...prev, { id, message, type }])

        // Auto remove after 3 seconds
        setTimeout(() => {
            setToasts((prev) => prev.filter((t) => t.id !== id))
        }, 3000)
    }, [])

    // Listen for global toast events
    useEffect(() => {
        const handleShowToast = (e: CustomEvent) => {
            const { message, type } = e.detail
            showToast(message, type)
        }

        window.addEventListener('show-toast', handleShowToast as EventListener)
        return () => window.removeEventListener('show-toast', handleShowToast as EventListener)
    }, [showToast])

    const removeToast = (id: number) => {
        setToasts((prev) => prev.filter((t) => t.id !== id))
    }

    const getToastStyle = (type: Toast['type']) => {
        switch (type) {
            case 'success':
                return 'bg-green-50 border-green-200 text-green-700'
            case 'error':
                return 'bg-red-50 border-red-200 text-red-700'
            case 'warning':
                return 'bg-yellow-50 border-yellow-200 text-yellow-700'
            default:
                return 'bg-primary-50 border-primary-200 text-primary-700'
        }
    }

    const getToastIcon = (type: Toast['type']) => {
        switch (type) {
            case 'success':
                return (
                    <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                )
            case 'error':
                return (
                    <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                )
            case 'warning':
                return (
                    <svg className="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                )
            default:
                return (
                    <svg className="w-5 h-5 text-primary-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                )
        }
    }

    return (
        <ToastContext.Provider value={{ showToast }}>
            {children}
            {/* Toast container */}
            <div className="fixed bottom-6 right-6 z-50 flex flex-col gap-3 pointer-events-none">
                {toasts.map((toast) => (
                    <div
                        key={toast.id}
                        className={`
                            glass rounded-xl p-4 flex items-center gap-3 min-w-[280px]
                            shadow-glass-lg animate-slide-up
                            pointer-events-auto
                            ${getToastStyle(toast.type)}
                        `}
                    >
                        {getToastIcon(toast.type)}
                        <span className="font-medium">{toast.message}</span>
                        <button
                            onClick={() => removeToast(toast.id)}
                            className="ml-auto text-current opacity-60 hover:opacity-100 transition-opacity"
                        >
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>
                ))}
            </div>
        </ToastContext.Provider>
    )
}

export function useToast() {
    const context = useContext(ToastContext)
    if (!context) {
        throw new Error('useToast must be used within a ToastProvider')
    }
    return context
}

// Global toast instance (for use outside components)
let globalShowToast: ((message: string, type?: Toast['type']) => void) | null = null

export const setGlobalToast = (fn: (message: string, type?: Toast['type']) => void) => {
    globalShowToast = fn
}

export const showToast = (message: string, type: Toast['type'] = 'info') => {
    if (globalShowToast) {
        globalShowToast(message, type)
    } else if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('show-toast', { detail: { message, type } }))
    }
}
