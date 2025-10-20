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
        'osx-temperature-sensor': 'commonjs osx-temperature-sensor',
        // Exclude Docker and native dependencies from server bundle
        'dockerode': 'commonjs dockerode',
        'ssh2': 'commonjs ssh2',
        'cpu-features': 'commonjs cpu-features'
      })
    } else {
      // Exclude server-only packages from client bundle
      config.resolve = config.resolve || {}
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
        child_process: false,
        ssh2: false,
        dockerode: false,
        'cpu-features': false
      }
    }

    // Ignore warnings for optional dependencies
    config.ignoreWarnings = [
      { module: /osx-temperature-sensor/ },
      { module: /ssh2/ },
      { module: /cpu-features/ },
      { module: /sshcrypto\.node/ }
    ]

    return config
  },
}

export default nextConfig
