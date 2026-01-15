'use client'

interface LoadingSpinnerProps {
    size?: 'sm' | 'md' | 'lg'
    text?: string
}

export default function LoadingSpinner({ size = 'md', text }: LoadingSpinnerProps) {
    const sizeClasses = {
        sm: 'w-8 h-8',
        md: 'w-12 h-12',
        lg: 'w-16 h-16 md:w-20 md:h-20',
    }

    const textSize = {
        sm: 'text-sm',
        md: 'text-base md:text-lg',
        lg: 'text-lg md:text-xl',
    }

    return (
        <div className="flex flex-col items-center justify-center p-8">
            {/* Spinning ring */}
            <div className={`relative ${sizeClasses[size]} mb-4`}>
                <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
            </div>

            {/* Loading text */}
            {text && (
                <div className="flex space-x-1">
                    <span className={`text-text-primary font-medium ${textSize[size]}`}>{text}</span>
                    <span className={`animate-pulse ${textSize[size]}`}>.</span>
                    <span className={`animate-pulse ${textSize[size]}`} style={{ animationDelay: '0.2s' }}>.</span>
                    <span className={`animate-pulse ${textSize[size]}`} style={{ animationDelay: '0.4s' }}>.</span>
                </div>
            )}
        </div>
    )
}

// Skeleton card component
export function SkeletonCard() {
    return (
        <div className="minimal p-5 space-y-3">
            {/* Title skeleton */}
            <div className="skeleton h-5 md:h-6 w-3/4 rounded"></div>
            {/* Subtitle skeleton */}
            <div className="skeleton h-4 w-1/2 rounded"></div>
            {/* Detail skeleton */}
            <div className="skeleton h-4 w-full rounded"></div>
        </div>
    )
}

// Full page loader component
export function FullPageLoader({ text }: { text?: string }) {
    return (
        <div className="fixed inset-0 bg-white/90 backdrop-blur-md flex items-center justify-center z-50">
            <div className="flex flex-col items-center">
                <div className="relative w-16 h-16 md:w-20 md:h-20 mb-6">
                    <div className="absolute inset-0 border-4 border-slate-200 rounded-full"></div>
                    <div className="absolute inset-0 border-4 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                </div>
                <div className="flex space-x-2">
                    <span className="text-text-primary font-medium text-lg md:text-xl">{text}</span>
                    <span className="animate-pulse text-lg md:text-xl">.</span>
                    <span className="animate-pulse text-lg md:text-xl" style={{ animationDelay: '0.2s' }}>.</span>
                    <span className="animate-pulse text-lg md:text-xl" style={{ animationDelay: '0.4s' }}>.</span>
                </div>
            </div>
        </div>
    )
}

// Small loading dots indicator
export function LoadingDots() {
    return (
        <div className="flex space-x-1">
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
            <div className="w-2 h-2 bg-primary-500 rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
        </div>
    )
}
