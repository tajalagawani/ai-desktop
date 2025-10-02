"use client"

import React, { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Carousel, Card as CarouselCard } from "@/components/ui/apple-cards-carousel"
import { motion, AnimatePresence } from "framer-motion"
import { 
  Search, Star, Download, Play, ChevronRight, Filter, Grid, 
  Smartphone, Gamepad2, Camera, Music, Video, Book, 
  Calculator, Globe, Shield, Zap, Palette, Code, 
  Heart, Briefcase, GraduationCap, ShoppingCart,
  TrendingUp, Award, Clock, Users, Eye, ThumbsUp,
  X, ArrowLeft, Share, MoreHorizontal, Settings
} from "lucide-react"

interface App {
  id: string
  name: string
  developer: string
  description: string
  category: string
  icon: string
  installed: boolean
  rating: number
  reviews: number
  price: number
  originalPrice?: number
  size: string
  version: string
  featured: boolean
  trending: boolean
  editorChoice: boolean
  screenshots: string[]
  ageRating: string
  languages: string[]
  lastUpdated: string
  downloads: string
  tags: string[]
  permissions: string[]
  whatsNew: string[]
}

const categoryIcons = {
  "All": Globe,
  "Productivity": Briefcase,
  "Games": Gamepad2,
  "Entertainment": Video,
  "Photo & Video": Camera,
  "Music": Music,
  "Social": Users,
  "Education": GraduationCap,
  "Shopping": ShoppingCart,
  "Business": TrendingUp,
  "Developer Tools": Code,
  "Graphics & Design": Palette,
  "Health & Fitness": Heart,
  "Utilities": Calculator,
  "Security": Shield,
  "News": Book,
  "Travel": Globe
}

const mockApps: App[] = [
  {
    id: "notion",
    name: "Notion",
    developer: "Notion Labs, Inc.",
    description: "Write, plan, share, and organize your work in one beautiful space. Notion is the connected workspace where better, faster work happens.",
    category: "Productivity",
    icon: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=100&h=100&fit=crop&crop=center",
    installed: false,
    rating: 4.8,
    reviews: 125000,
    price: 0,
    originalPrice: 8,
    size: "145 MB",
    version: "3.1.0",
    featured: true,
    trending: true,
    editorChoice: true,
    screenshots: [
      "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1586281380349-632531db7ed4?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1587440871875-191322ee64b0?w=800&h=600&fit=crop"
    ],
    ageRating: "4+",
    languages: ["English", "Spanish", "French", "German", "Japanese"],
    lastUpdated: "2024-09-15",
    downloads: "50M+",
    tags: ["Note-taking", "Organization", "Team collaboration"],
    permissions: ["Internet", "Storage", "Notifications"],
    whatsNew: [
      "New AI writing assistant",
      "Improved collaboration features",
      "Bug fixes and performance improvements"
    ]
  },
  {
    id: "figma",
    name: "Figma",
    developer: "Figma, Inc.",
    description: "Figma is the leading collaborative design tool for building meaningful products. Seamlessly design, prototype, develop, and collect feedback in a single platform.",
    category: "Graphics & Design",
    icon: "https://images.unsplash.com/photo-1609921212029-bb5a28e60960?w=100&h=100&fit=crop&crop=center",
    installed: true,
    rating: 4.9,
    reviews: 98000,
    price: 0,
    size: "234 MB",
    version: "116.15.4",
    featured: true,
    trending: false,
    editorChoice: true,
    screenshots: [
      "https://images.unsplash.com/photo-1609921212029-bb5a28e60960?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1558655146-d09347e92766?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1586717791821-3f44a563fa4c?w=800&h=600&fit=crop"
    ],
    ageRating: "4+",
    languages: ["English", "Spanish", "French", "German", "Portuguese"],
    lastUpdated: "2024-09-20",
    downloads: "25M+",
    tags: ["Design", "Prototyping", "Collaboration", "UI/UX"],
    permissions: ["Internet", "Storage", "Camera"],
    whatsNew: [
      "Enhanced prototyping features",
      "New component variants",
      "Performance optimizations"
    ]
  },
  {
    id: "discord",
    name: "Discord",
    developer: "Discord Inc.",
    description: "Discord is the easiest way to talk over voice, video, and text. Talk, chat, hang out, and stay close with your friends and communities.",
    category: "Social",
    icon: "https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?w=100&h=100&fit=crop&crop=center",
    installed: false,
    rating: 4.7,
    reviews: 2100000,
    price: 0,
    size: "189 MB",
    version: "0.0.291",
    featured: true,
    trending: true,
    editorChoice: false,
    screenshots: [
      "https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1611262588024-d12430b98920?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1606318801954-d46d46d3360a?w=800&h=600&fit=crop"
    ],
    ageRating: "13+",
    languages: ["English", "Spanish", "French", "German", "Japanese", "Korean"],
    lastUpdated: "2024-09-25",
    downloads: "500M+",
    tags: ["Chat", "Voice", "Gaming", "Communities"],
    permissions: ["Internet", "Microphone", "Camera", "Notifications"],
    whatsNew: [
      "New voice channels features",
      "Improved mobile experience",
      "Bug fixes"
    ]
  },
  {
    id: "spotify",
    name: "Spotify",
    developer: "Spotify AB",
    description: "Spotify is a digital music service that gives you access to millions of songs, podcasts and videos from artists all over the world.",
    category: "Music",
    icon: "https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?w=100&h=100&fit=crop&crop=center",
    installed: true,
    rating: 4.6,
    reviews: 5600000,
    price: 0,
    originalPrice: 9.99,
    size: "156 MB",
    version: "8.8.96.1013",
    featured: true,
    trending: false,
    editorChoice: false,
    screenshots: [
      "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1470225620780-dba8ba36b745?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1445985543470-41fba5c3144a?w=800&h=600&fit=crop"
    ],
    ageRating: "12+",
    languages: ["English", "Spanish", "French", "German", "Italian", "Portuguese"],
    lastUpdated: "2024-09-22",
    downloads: "1B+",
    tags: ["Music", "Podcasts", "Streaming", "Playlists"],
    permissions: ["Internet", "Storage", "Microphone"],
    whatsNew: [
      "Enhanced podcast experience",
      "New discovery features",
      "Improved audio quality"
    ]
  },
  {
    id: "minecraft",
    name: "Minecraft",
    developer: "Mojang Studios",
    description: "Explore infinite worlds and build everything from the simplest of homes to the grandest of castles in the creative sandbox game.",
    category: "Games",
    icon: "https://images.unsplash.com/photo-1606459679694-e8d7b9eeb0e4?w=100&h=100&fit=crop&crop=center",
    installed: false,
    rating: 4.5,
    reviews: 3200000,
    price: 26.95,
    size: "1.2 GB",
    version: "1.20.4",
    featured: true,
    trending: true,
    editorChoice: true,
    screenshots: [
      "https://images.unsplash.com/photo-1606459679694-e8d7b9eeb0e4?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=800&h=600&fit=crop"
    ],
    ageRating: "7+",
    languages: ["English", "Spanish", "French", "German", "Japanese", "Chinese"],
    lastUpdated: "2024-09-18",
    downloads: "300M+",
    tags: ["Sandbox", "Creativity", "Multiplayer", "Adventure"],
    permissions: ["Internet", "Storage"],
    whatsNew: [
      "New biomes and mobs",
      "Updated crafting recipes",
      "Performance improvements"
    ]
  },
  {
    id: "zoom",
    name: "Zoom",
    developer: "Zoom Video Communications",
    description: "Zoom is a leading video conferencing platform that connects people through frictionless video, voice, chat, and content sharing.",
    category: "Business",
    icon: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=100&h=100&fit=crop&crop=center",
    installed: true,
    rating: 4.4,
    reviews: 890000,
    price: 0,
    originalPrice: 14.99,
    size: "67 MB",
    version: "5.16.5",
    featured: false,
    trending: false,
    editorChoice: false,
    screenshots: [
      "https://images.unsplash.com/photo-1588196749597-9ff075ee6b5b?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1587825140708-dfaf72ae4b04?w=800&h=600&fit=crop",
      "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&h=600&fit=crop"
    ],
    ageRating: "4+",
    languages: ["English", "Spanish", "French", "German", "Chinese", "Japanese"],
    lastUpdated: "2024-09-10",
    downloads: "1B+",
    tags: ["Video conferencing", "Meetings", "Webinars", "Chat"],
    permissions: ["Internet", "Camera", "Microphone", "Notifications"],
    whatsNew: [
      "AI-powered meeting summaries",
      "Enhanced security features",
      "Improved mobile experience"
    ]
  }
]

const DummyContent = ({ title, description }: { title: string; description: string }) => {
  return (
    <div className="bg-gradient-to-br from-white to-gray-50 dark:from-neutral-800 dark:to-neutral-900 p-8 md:p-14 rounded-3xl mb-4 border border-gray-100 dark:border-neutral-700">
      <p className="text-neutral-600 dark:text-neutral-400 text-base md:text-2xl font-sans max-w-3xl mx-auto leading-relaxed">
        <span className="font-bold text-neutral-700 dark:text-neutral-200 text-xl md:text-3xl block mb-4">
          {title}
        </span>
        {description}
      </p>
    </div>
  );
};

const carouselData = [
  {
    category: "Editor's Choice",
    title: "Notion",
    src: "https://images.unsplash.com/photo-1611224923853-80b023f02d71?w=800&h=600&fit=crop",
    content: <DummyContent 
      title="Transform your workflow with Notion"
      description="The all-in-one workspace where you can write, plan, and get organized. Perfect for teams and individuals who want to stay productive."
    />
  },
  {
    category: "Trending Now",
    title: "Figma",
    src: "https://images.unsplash.com/photo-1609921212029-bb5a28e60960?w=800&h=600&fit=crop",
    content: <DummyContent 
      title="Design the future with Figma"
      description="Collaborative design tool that brings teams together to create, prototype, and build better products faster than ever before."
    />
  },
  {
    category: "Popular",
    title: "Discord",
    src: "https://images.unsplash.com/photo-1614680376573-df3480f0c6ff?w=800&h=600&fit=crop",
    content: <DummyContent 
      title="Connect with Discord"
      description="Join millions of users in voice, video, and text conversations. Build communities and stay connected with friends worldwide."
    />
  },
  {
    category: "Entertainment",
    title: "Spotify",
    src: "https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?w=800&h=600&fit=crop",
    content: <DummyContent 
      title="Discover music on Spotify"
      description="Stream millions of songs, podcasts, and audiobooks. Discover new artists and create the perfect playlist for every moment."
    />
  },
  {
    category: "Gaming",
    title: "Minecraft",
    src: "https://images.unsplash.com/photo-1606459679694-e8d7b9eeb0e4?w=800&h=600&fit=crop",
    content: <DummyContent 
      title="Build infinite worlds in Minecraft"
      description="Unleash your creativity in this sandbox world. Build, explore, and survive in randomly generated worlds full of possibilities."
    />
  }
]

export function MacAppStore() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("All")
  const [apps, setApps] = useState(mockApps)
  const [selectedApp, setSelectedApp] = useState<App | null>(null)
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid")
  const [sortBy, setSortBy] = useState<"featured" | "rating" | "recent" | "name">("featured")
  const [showFilters, setShowFilters] = useState(false)
  const [selectedScreenshot, setSelectedScreenshot] = useState(0)

  const categories = Object.keys(categoryIcons)

  const filteredApps = apps.filter((app) => {
    const matchesSearch =
      app.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.developer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      app.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesCategory = selectedCategory === "All" || app.category === selectedCategory

    return matchesSearch && matchesCategory
  }).sort((a, b) => {
    switch (sortBy) {
      case "rating":
        return b.rating - a.rating
      case "recent":
        return new Date(b.lastUpdated).getTime() - new Date(a.lastUpdated).getTime()
      case "name":
        return a.name.localeCompare(b.name)
      default:
        return (b.featured ? 1 : 0) - (a.featured ? 1 : 0)
    }
  })

  const featuredApps = apps.filter((app) => app.featured)
  const trendingApps = apps.filter((app) => app.trending)
  const editorChoiceApps = apps.filter((app) => app.editorChoice)

  const installApp = (appId: string) => {
    setApps((prev) => prev.map((app) => (app.id === appId ? { ...app, installed: true } : app)))
  }

  const uninstallApp = (appId: string) => {
    setApps((prev) => prev.map((app) => (app.id === appId ? { ...app, installed: false } : app)))
  }

  const formatPrice = (price: number) => {
    return price === 0 ? "Free" : `$${price.toFixed(2)}`
  }

  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + "M"
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + "K"
    }
    return num.toString()
  }

  if (selectedApp) {
    return (
      <div className="h-full bg-gradient-to-br from-blue-50 to-white dark:from-neutral-900 dark:to-neutral-800 overflow-auto">
        <div className="max-w-6xl mx-auto p-6">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <Button 
              variant="ghost" 
              onClick={() => setSelectedApp(null)}
              className="flex items-center gap-2 hover:bg-white/50 dark:hover:bg-neutral-800/50"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Store
            </Button>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Share className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm">
                <MoreHorizontal className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* App Header */}
          <div className="bg-white dark:bg-neutral-800 rounded-3xl p-8 mb-8 shadow-lg border border-gray-100 dark:border-neutral-700">
            <div className="flex flex-col lg:flex-row gap-8">
              <div className="flex-shrink-0">
                <img 
                  src={selectedApp.icon} 
                  alt={selectedApp.name}
                  className="w-32 h-32 rounded-3xl shadow-lg"
                />
              </div>
              <div className="flex-1">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-4xl font-bold mb-2">{selectedApp.name}</h1>
                    <p className="text-xl text-gray-600 dark:text-gray-300 mb-1">{selectedApp.developer}</p>
                    <p className="text-gray-500 dark:text-gray-400">{selectedApp.category}</p>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {selectedApp.editorChoice && (
                      <Badge className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                        <Award className="h-3 w-3 mr-1" />
                        Editor's Choice
                      </Badge>
                    )}
                    {selectedApp.trending && (
                      <Badge variant="secondary">
                        <TrendingUp className="h-3 w-3 mr-1" />
                        Trending
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-6 mb-6">
                  <div className="flex items-center gap-2">
                    <div className="flex items-center">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`h-5 w-5 ${i < Math.floor(selectedApp.rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'}`} 
                        />
                      ))}
                    </div>
                    <span className="font-semibold text-lg">{selectedApp.rating}</span>
                    <span className="text-gray-500">({formatNumber(selectedApp.reviews)} reviews)</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-500">
                    <Download className="h-4 w-4" />
                    <span>{selectedApp.downloads}</span>
                  </div>
                  <Badge variant="outline">{selectedApp.ageRating}</Badge>
                </div>

                <div className="flex flex-col sm:flex-row gap-4">
                  {selectedApp.installed ? (
                    <div className="flex gap-2">
                      <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600">
                        <Play className="h-5 w-5 mr-2" />
                        Open
                      </Button>
                      <Button size="lg" variant="outline" onClick={() => uninstallApp(selectedApp.id)}>
                        Uninstall
                      </Button>
                    </div>
                  ) : (
                    <Button 
                      size="lg" 
                      className="bg-gradient-to-r from-green-500 to-blue-500 hover:from-green-600 hover:to-blue-600 px-8"
                      onClick={() => installApp(selectedApp.id)}
                    >
                      <Download className="h-5 w-5 mr-2" />
                      {formatPrice(selectedApp.price)}
                      {selectedApp.originalPrice && (
                        <span className="ml-2 line-through text-sm opacity-70">
                          ${selectedApp.originalPrice}
                        </span>
                      )}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Screenshots */}
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Screenshots</h2>
            <div className="flex gap-4 overflow-x-auto pb-4">
              {selectedApp.screenshots.map((screenshot, index) => (
                <motion.img
                  key={index}
                  src={screenshot}
                  alt={`${selectedApp.name} screenshot ${index + 1}`}
                  className="w-80 h-60 object-cover rounded-2xl cursor-pointer shadow-lg"
                  whileHover={{ scale: 1.05 }}
                  onClick={() => setSelectedScreenshot(index)}
                />
              ))}
            </div>
          </div>

          {/* Description & Details */}
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2 space-y-8">
              <div className="bg-white dark:bg-neutral-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-neutral-700">
                <h2 className="text-2xl font-bold mb-4">About {selectedApp.name}</h2>
                <p className="text-gray-700 dark:text-gray-300 leading-relaxed text-lg">
                  {selectedApp.description}
                </p>
              </div>

              {selectedApp.whatsNew.length > 0 && (
                <div className="bg-white dark:bg-neutral-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-neutral-700">
                  <h2 className="text-2xl font-bold mb-4">What's New</h2>
                  <ul className="space-y-3">
                    {selectedApp.whatsNew.map((item, index) => (
                      <li key={index} className="flex items-start gap-3">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-3 flex-shrink-0" />
                        <span className="text-gray-700 dark:text-gray-300">{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="bg-white dark:bg-neutral-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-neutral-700">
                <h3 className="text-xl font-bold mb-4">Information</h3>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Version</span>
                    <span className="font-medium">{selectedApp.version}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Size</span>
                    <span className="font-medium">{selectedApp.size}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Updated</span>
                    <span className="font-medium">{selectedApp.lastUpdated}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600 dark:text-gray-400">Age Rating</span>
                    <span className="font-medium">{selectedApp.ageRating}</span>
                  </div>
                </div>
              </div>

              <div className="bg-white dark:bg-neutral-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-neutral-700">
                <h3 className="text-xl font-bold mb-4">Languages</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedApp.languages.map((lang) => (
                    <Badge key={lang} variant="outline">{lang}</Badge>
                  ))}
                </div>
              </div>

              <div className="bg-white dark:bg-neutral-800 rounded-2xl p-6 shadow-lg border border-gray-100 dark:border-neutral-700">
                <h3 className="text-xl font-bold mb-4">Tags</h3>
                <div className="flex flex-wrap gap-2">
                  {selectedApp.tags.map((tag) => (
                    <Badge key={tag} variant="secondary">{tag}</Badge>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full flex flex-col bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-neutral-900 dark:via-neutral-800 dark:to-neutral-900">
      {/* Header */}
      <div className="sticky top-0 bg-white/80 dark:bg-neutral-800/80 backdrop-blur-xl border-b border-gray-200 dark:border-neutral-700 z-50">
        <div className="p-6">
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                App Store
              </h1>
              <div className="flex items-center gap-2">
                <Button
                  variant={viewMode === "grid" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("grid")}
                >
                  <Grid className="h-4 w-4" />
                </Button>
                <Button
                  variant={viewMode === "list" ? "default" : "outline"}
                  size="sm"
                  onClick={() => setViewMode("list")}
                >
                  <Users className="h-4 w-4" />
                </Button>
              </div>
            </div>
            
            <div className="flex items-center gap-4 w-full lg:w-auto">
              <div className="relative flex-1 lg:w-96">
                <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <Input
                  placeholder="Search for apps, games, and more..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-12 bg-white dark:bg-neutral-800 border-gray-200 dark:border-neutral-700 rounded-full h-12 shadow-sm"
                />
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowFilters(!showFilters)}
                className="rounded-full"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </Button>
            </div>
          </div>

          {/* Filters */}
          <AnimatePresence>
            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 p-4 bg-gray-50 dark:bg-neutral-700 rounded-2xl"
              >
                <div className="flex flex-wrap gap-4">
                  <div className="flex items-center gap-2">
                    <span className="text-sm font-medium">Sort by:</span>
                    <select
                      value={sortBy}
                      onChange={(e) => setSortBy(e.target.value as any)}
                      className="rounded-lg border border-gray-200 dark:border-neutral-600 bg-white dark:bg-neutral-800 px-3 py-1 text-sm"
                    >
                      <option value="featured">Featured</option>
                      <option value="rating">Rating</option>
                      <option value="recent">Recently Updated</option>
                      <option value="name">Name</option>
                    </select>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Categories */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-neutral-700 bg-white/50 dark:bg-neutral-800/50">
        <div className="flex gap-2 overflow-x-auto scrollbar-hide">
          {categories.map((category) => {
            const IconComponent = categoryIcons[category as keyof typeof categoryIcons]
            return (
              <Button
                key={category}
                variant={selectedCategory === category ? "default" : "ghost"}
                size="sm"
                className={`flex items-center gap-2 whitespace-nowrap rounded-full ${
                  selectedCategory === category 
                    ? "bg-gradient-to-r from-blue-500 to-purple-500 text-white" 
                    : "hover:bg-gray-100 dark:hover:bg-neutral-700"
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                <IconComponent className="h-4 w-4" />
                {category}
              </Button>
            )
          })}
        </div>
      </div>

      {/* Tab content is now handled by the Aceternity Tabs component */}
    </div>
  )
}