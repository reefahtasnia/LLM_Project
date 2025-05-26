/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false, // Reduce strict mode overhead
  swcMinify: true, // Faster minification
  compiler: {
    removeConsole: true, // Save memory
  }
}

export default nextConfig