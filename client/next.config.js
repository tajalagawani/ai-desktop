/** @type {import('next').NextConfig} */
const nextConfig = {
  // Static export configuration
  output: 'export',

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Trailing slash for better CDN compatibility
  trailingSlash: true,

  // Asset prefix for CDN (optional)
  // assetPrefix: process.env.NEXT_PUBLIC_CDN_URL || '',

  // Base path (if deploying to subdirectory)
  // basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',

  // Disable server features
  experimental: {
    // Runtime configuration
  },

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://92.112.181.127',
    NEXT_PUBLIC_WS_URL: process.env.NEXT_PUBLIC_WS_URL || 'http://92.112.181.127',
  },

  // Webpack configuration
  webpack: (config, { isServer }) => {
    // Optimize bundle size
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }

    return config
  },

  // Compression
  compress: true,

  // React strict mode
  reactStrictMode: true,

  // SWC minification
  swcMinify: true,
}

module.exports = nextConfig
