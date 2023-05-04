/* eslint-disable import/no-extraneous-dependencies */
import { defineConfig } from 'vite';
import preact from '@preact/preset-vite';
import { viteSingleFile } from 'vite-plugin-singlefile';
import path from 'path';

export default defineConfig({
  server: {
    port: 8080,
  },
  resolve: {
    alias: {
      react: 'preact/compat',
      'react-dom': 'preact/compat',
      '~': path.join(__dirname, 'src'),
    },
  },
  plugins: [preact(), viteSingleFile()],
});
