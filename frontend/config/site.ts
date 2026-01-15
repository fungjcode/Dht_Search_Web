// 网站配置文件
export const siteConfig = {
    // 网站基本信息（国际化）
    name: 'DHT Search',
    title: {
        zh: 'DHT Search - 开源种子搜索引擎',
        en: 'DHT Search - Open Source Torrent Search Engine',
    },
    description: {
        zh: '基于 DHT 网络的开源种子搜索引擎，提供快速、准确的种子搜索服务',
        en: 'Open source torrent search engine based on DHT network, providing fast and accurate search services',
    },
    keywords: 'DHT, 种子搜索, BT搜索, 磁力链接, torrent search, bt, magnet',

    // 网站 URL
    url: 'https://example.com', // 生产环境域名
    apiUrl: process.env.NEXT_PUBLIC_API_URL || 'https://example.com',

    // SEO 配置
    seo: {
        defaultTitle: {
            zh: 'DHT Search - 开源种子搜索引擎',
            en: 'DHT Search - Open Source Torrent Search Engine',
        },
        titleTemplate: '%s | DHT Search',  // 标题模板，%s 为页面标题占位符
        defaultDescription: {
            zh: '基于 DHT 网络的开源种子搜索引擎，提供快速、准确的种子搜索服务',
            en: 'Open source torrent search engine based on DHT network, providing fast and accurate search services',
        },
        // 搜索页标题模板
        searchTitleTemplate: {
            zh: '%s - %s',           // 格式: 搜索内容 - 网站名
            en: '%s - %s',           // 格式: 搜索内容 - 网站名
        },
        // 详情页标题模板
        detailTitleTemplate: {
            zh: '%s - %s',           // 格式: 种子名 - 网站名
            en: '%s - %s',           // 格式: 种子名 - 网站名
        },
        openGraph: {
            type: 'website',
            locale: 'zh_CN',
            url: 'https://example.com',
            siteName: 'DHT Search',
        },
        twitter: {
            handle: '@dhtsearch',
            site: '@dhtsearch',
            cardType: 'summary_large_image',
        },
    },

    // 联系信息
    contact: {
        email: 'admin@example.com',
        github: 'https://github.com/yourusername/dht-search',
    },

    // 功能开关
    features: {
        enableRecommendations: true,
        enableDMCA: true,
        enableI18n: true,
    },

    // 分页配置
    pagination: {
        defaultPageSize: 20,
        maxPageSize: 100,
    },

    // 搜索配置
    search: {
        minKeywordLength: 2,
        maxKeywordLength: 100,
        defaultSort: 'time',
        sortOptions: [
            { value: 'time', label: { zh: '最新', en: 'Newest' } },
            { value: 'health', label: { zh: '健康度', en: 'Health' } },
            { value: 'hot', label: { zh: '热度', en: 'Popular' } },
            { value: 'size', label: { zh: '大小', en: 'Size' } },
            { value: 'relevance', label: { zh: '相关度', en: 'Relevance' } },
        ],
    },
}

export default siteConfig
