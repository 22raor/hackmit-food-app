import type { NextConfig } from "next";

const withPWA = require('next-pwa')({
  dest: 'public'
});

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
};

export default withPWA(nextConfig);
