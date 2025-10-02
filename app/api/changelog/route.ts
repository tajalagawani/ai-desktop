import { NextResponse } from 'next/server'

export async function GET() {
  try {
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

    return NextResponse.json({
      success: true,
      changelog,
      latest: changelog[0]?.sha || null,
    })
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Failed to fetch changelog' },
      { status: 500 }
    )
  }
}
