/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable strict mode for better development experience
  reactStrictMode: true,

  // Image optimization (disable for VPS without image optimization service)
  images: {
    unoptimized: true,
  },

  // Output standalone for VPS deployment
  output: 'standalone',

  // Disable powered by header for security
  poweredByHeader: false,

  // TODO: Fix TypeScript errors and remove this
  typescript: {
    ignoreBuildErrors: true,
  },

  // Webpack config
  webpack: (config, { isServer }) => {
    if (isServer) {
      // Ignore optional macOS dependencies on Linux VPS
      config.externals = config.externals || []
      config.externals.push({
        'osx-temperature-sensor': 'commonjs osx-temperature-sensor'
      })
    }

    // Ignore warnings for optional dependencies
    config.ignoreWarnings = [
      { module: /osx-temperature-sensor/ }
    ]

    return config
  },
}

export default nextConfig
