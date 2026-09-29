import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // e2e runs a second dev server alongside the regular one; it needs its own build dir (and lock).
  distDir: process.env.NEXT_DIST_DIR || ".next",
};

export default nextConfig;
