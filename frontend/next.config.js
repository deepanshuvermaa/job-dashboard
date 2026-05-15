/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  output: 'standalone',
  generateBuildId: () => `v${Date.now()}`,
}

module.exports = nextConfig
