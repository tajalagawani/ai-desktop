import fs from 'fs/promises'
import path from 'path'
import { FrameworkDetection, FrameworkType } from './types'

export async function detectFramework(repoPath: string): Promise<FrameworkDetection> {
  try {
    // Check for package.json (Node.js projects)
    const packageJsonPath = path.join(repoPath, 'package.json')
    if (await fileExists(packageJsonPath)) {
      const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'))
      return detectNodeFramework(packageJson)
    }

    // Check for Python projects
    const requirementsPath = path.join(repoPath, 'requirements.txt')
    if (await fileExists(requirementsPath)) {
      return await detectPythonFramework(repoPath)
    }

    // Check for PHP projects
    const composerPath = path.join(repoPath, 'composer.json')
    if (await fileExists(composerPath)) {
      return await detectPHPFramework(repoPath)
    }

    // Check for static site
    const indexHtmlPath = path.join(repoPath, 'index.html')
    if (await fileExists(indexHtmlPath)) {
      return {
        type: 'static',
        buildCommand: null,
        startCommand: 'npx serve -s . -l 3000',
        installCommand: 'npm install -g serve',
        port: 3000
      }
    }

    // Default to Node.js
    return {
      type: 'node',
      buildCommand: null,
      startCommand: 'npm start',
      installCommand: 'npm install',
      port: 3000
    }
  } catch (error) {
    console.error('Error detecting framework:', error)
    throw new Error('Failed to detect project framework')
  }
}

function detectNodeFramework(packageJson: any): FrameworkDetection {
  const deps = { ...packageJson.dependencies, ...packageJson.devDependencies }
  const scripts = packageJson.scripts || {}

  // Next.js
  if (deps.next) {
    return {
      type: 'nextjs',
      version: deps.next,
      buildCommand: 'npm run build',
      startCommand: 'npm start',
      installCommand: 'npm install',
      outputDir: '.next',
      port: 3000
    }
  }

  // Nuxt.js
  if (deps.nuxt) {
    return {
      type: 'nuxt',
      version: deps.nuxt,
      buildCommand: 'npm run build',
      startCommand: 'npm start',
      installCommand: 'npm install',
      outputDir: '.nuxt',
      port: 3000
    }
  }

  // Vite (React, Vue, Svelte)
  if (deps.vite) {
    if (deps.react) {
      return {
        type: 'react-vite',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
    if (deps.vue) {
      return {
        type: 'vue',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
    if (deps.svelte) {
      return {
        type: 'svelte',
        buildCommand: 'npm run build',
        startCommand: 'npx serve -s dist -l 3000',
        installCommand: 'npm install',
        outputDir: 'dist',
        port: 3000
      }
    }
  }

  // Create React App
  if (deps['react-scripts']) {
    return {
      type: 'react-cra',
      buildCommand: 'npm run build',
      startCommand: 'npx serve -s build -l 3000',
      installCommand: 'npm install',
      outputDir: 'build',
      port: 3000
    }
  }

  // Angular
  if (deps['@angular/core']) {
    return {
      type: 'angular',
      buildCommand: 'npm run build',
      startCommand: 'npx serve -s dist -l 3000',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // Astro
  if (deps.astro) {
    return {
      type: 'astro',
      buildCommand: 'npm run build',
      startCommand: 'npm start',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // NestJS
  if (deps['@nestjs/core']) {
    return {
      type: 'nestjs',
      buildCommand: 'npm run build',
      startCommand: 'npm run start:prod',
      installCommand: 'npm install',
      outputDir: 'dist',
      port: 3000
    }
  }

  // Express (check for express in dependencies or common patterns)
  if (deps.express) {
    return {
      type: 'express',
      buildCommand: null,
      startCommand: scripts.start || 'node server.js',
      installCommand: 'npm install',
      port: 3000
    }
  }

  // Generic Node.js
  return {
    type: 'node',
    buildCommand: scripts.build || null,
    startCommand: scripts.start || 'node index.js',
    installCommand: 'npm install',
    port: 3000
  }
}

async function detectPythonFramework(repoPath: string): Promise<FrameworkDetection> {
  // Check for Django
  const managePyPath = path.join(repoPath, 'manage.py')
  if (await fileExists(managePyPath)) {
    return {
      type: 'django',
      buildCommand: null,
      startCommand: 'python manage.py runserver 0.0.0.0:8000',
      installCommand: 'pip install -r requirements.txt',
      port: 8000
    }
  }

  // Check for Flask (look for app.py or main.py with Flask import)
  const appPyPath = path.join(repoPath, 'app.py')
  const mainPyPath = path.join(repoPath, 'main.py')

  if (await fileExists(appPyPath)) {
    const content = await fs.readFile(appPyPath, 'utf-8')
    if (content.includes('from flask import') || content.includes('import flask')) {
      return {
        type: 'flask',
        buildCommand: null,
        startCommand: 'python app.py',
        installCommand: 'pip install -r requirements.txt',
        port: 5000
      }
    }
  }

  // Check for FastAPI
  if (await fileExists(mainPyPath)) {
    const content = await fs.readFile(mainPyPath, 'utf-8')
    if (content.includes('from fastapi import') || content.includes('import fastapi')) {
      return {
        type: 'fastapi',
        buildCommand: null,
        startCommand: 'uvicorn main:app --host 0.0.0.0 --port 8000',
        installCommand: 'pip install -r requirements.txt',
        port: 8000
      }
    }
  }

  // Default Python app
  return {
    type: 'flask',
    buildCommand: null,
    startCommand: 'python app.py',
    installCommand: 'pip install -r requirements.txt',
    port: 5000
  }
}

async function detectPHPFramework(repoPath: string): Promise<FrameworkDetection> {
  const composerJson = JSON.parse(
    await fs.readFile(path.join(repoPath, 'composer.json'), 'utf-8')
  )

  // Laravel
  if (composerJson.require?.['laravel/framework']) {
    return {
      type: 'laravel',
      buildCommand: 'composer install',
      startCommand: 'php artisan serve --host=0.0.0.0 --port=8000',
      installCommand: 'composer install',
      port: 8000
    }
  }

  // Symfony
  if (composerJson.require?.['symfony/framework-bundle']) {
    return {
      type: 'symfony',
      buildCommand: 'composer install',
      startCommand: 'symfony server:start --no-tls --port=8000',
      installCommand: 'composer install',
      port: 8000
    }
  }

  // Generic PHP
  return {
    type: 'static',
    buildCommand: null,
    startCommand: 'php -S 0.0.0.0:8000',
    installCommand: 'composer install',
    port: 8000
  }
}

async function fileExists(filePath: string): Promise<boolean> {
  try {
    await fs.access(filePath)
    return true
  } catch {
    return false
  }
}

