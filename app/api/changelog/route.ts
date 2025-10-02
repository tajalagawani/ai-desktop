import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'

export async function GET() {
  try {
    // Read current version from version.json
    const versionPath = path.join(process.cwd(), 'version.json')
    const versionData = JSON.parse(fs.readFileSync(versionPath, 'utf-8'))

    // Fetch recent commits from GitHub API
    const response = await fetch(
      'https://api.github.com/repos/tajalagawani/ai-desktop/commits?per_page=10',
      {
        headers: {
          'Accept': 'application/vnd.github.v3+json',
        },
        next: { revalidate: 60 } // Cache for 60 seconds
      }
    )

    if (!response.ok) {
      throw new Error('Failed to fetch commits')
    }

    const commits = await response.json()

    // Format commits for display
    const changelog = commits.map((commit: any) => ({
      sha: commit.sha.substring(0, 7),
      message: commit.commit.message.split('\n')[0], // First line only
      author: commit.commit.author.name,
      date: commit.commit.author.date,
      url: commit.html_url,
    }))

    // Check if update is available (compare current SHA with latest)
    const currentVersionSHA = versionData.currentSHA || null
    const latestSHA = commits[0]?.sha.substring(0, 7) || null
    const updateAvailable = currentVersionSHA !== latestSHA && currentVersionSHA !== null

    return NextResponse.json({
      success: true,
      currentVersion: versionData.version,
      buildDate: versionData.buildDate,
      currentSHA: currentVersionSHA,
      latestSHA,
      lastUpdated: versionData.lastUpdated || null,
      updateAvailable,
      changelog,
      versionChangelog: versionData.changelog,
    })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch changelog' },
      { status: 500 }
    )
  }
}
