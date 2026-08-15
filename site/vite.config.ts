import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig(() => {
  const repository = process.env.GITHUB_REPOSITORY?.split("/")[1];
  return {
    base: process.env.GITHUB_ACTIONS && repository ? `/${repository}/` : "/",
    plugins: [react()],
  };
});
