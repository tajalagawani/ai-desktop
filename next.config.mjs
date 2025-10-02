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
}

export default nextConfig
