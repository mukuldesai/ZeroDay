const path = require('path');

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: [],
  },
  webpack: (config) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@': path.resolve(__dirname),
      '@lib': path.resolve(__dirname, 'lib'),
      '@components': path.resolve(__dirname, 'components'),
    };
    return config;
  },
  typescript: {
    ignoreBuildErrors: false,
  },
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*', 
      },
    ];
  },
};

module.exports = nextConfig;
