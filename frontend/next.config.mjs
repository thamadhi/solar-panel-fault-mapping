/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    // API_URL is the server-side target for the same-origin /api-proxy
    // rewrite (recommended on Vercel). NEXT_PUBLIC_API_URL is the legacy/
    // Docker browser-side override. Local dev falls back to Flask's default.
    const apiUrl =
      process.env.API_URL || process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    return [
      {
        source: '/api-proxy/:path*',
        destination: `${apiUrl}/:path*`,
      },
    ];
  },
};

export default nextConfig;
