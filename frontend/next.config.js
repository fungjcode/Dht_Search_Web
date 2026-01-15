/** @type {import('next').NextConfig} */
const nextConfig = {
    reactStrictMode: true,

    // 环境变量
    env: {
        NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://example.com',
        NEXT_PUBLIC_SITE_URL: process.env.NEXT_PUBLIC_SITE_URL || 'https://example.com',
    },

    // 图片优化
    images: {
        domains: [],
    },
}

module.exports = nextConfig
