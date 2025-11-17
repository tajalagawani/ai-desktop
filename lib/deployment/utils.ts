import { FrameworkType } from './types'

export function getFrameworkDisplayName(type: FrameworkType): string {
  const names: Record<FrameworkType, string> = {
    'nextjs': 'Next.js',
    'react-vite': 'React (Vite)',
    'react-cra': 'React (Create React App)',
    'vue': 'Vue.js',
    'nuxt': 'Nuxt.js',
    'angular': 'Angular',
    'svelte': 'Svelte',
    'astro': 'Astro',
    'node': 'Node.js',
    'express': 'Express.js',
    'nestjs': 'NestJS',
    'django': 'Django',
    'flask': 'Flask',
    'fastapi': 'FastAPI',
    'laravel': 'Laravel',
    'symfony': 'Symfony',
    'static': 'Static HTML'
  }
  return names[type] || type
}
