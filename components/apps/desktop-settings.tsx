"use client"

import React, { useState } from "react"
import { Card } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Check } from "lucide-react"

interface DesktopSettingsProps {
  currentBackground: string
  onBackgroundChange: (bg: string) => void
}

const BACKGROUNDS = [
  {
    id: 'gradient-beige',
    name: 'Beige Waves',
    type: 'gradient',
    light: 'linear-gradient(135deg, #e8dcc8 0%, #f5f0e8 25%, #d4c4a8 50%, #e8d8c0 75%, #f2ebe0 100%)',
    dark: 'linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 50%, #252525 100%)',
    preview: '/backgrounds/beige-waves.jpg'
  },
  {
    id: 'image-abstract',
    name: 'Abstract Art',
    type: 'image',
    value: '/backgrounds/abstract-art.jpg',
    preview: '/backgrounds/abstract-art.jpg'
  }
]

export function DesktopSettings({ currentBackground, onBackgroundChange }: DesktopSettingsProps) {
  const [selectedBg, setSelectedBg] = useState(currentBackground)

  const handleSelect = (bgId: string) => {
    setSelectedBg(bgId)
    onBackgroundChange(bgId)
  }

  return (
    <div className="flex flex-col h-full p-6 overflow-auto">
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-semibold mb-2">Desktop Settings</h2>
          <p className="text-sm text-muted-foreground">
            Customize your desktop appearance
          </p>
        </div>

        <Tabs defaultValue="background" className="w-full">
          <TabsList>
            <TabsTrigger value="background">Background</TabsTrigger>
            <TabsTrigger value="appearance">Appearance</TabsTrigger>
          </TabsList>

          <TabsContent value="background" className="space-y-4 mt-4">
            <div>
              <Label className="text-base font-medium">Choose Background</Label>
              <p className="text-sm text-muted-foreground mb-4">
                Select a background for your desktop
              </p>

              <div className="grid grid-cols-2 gap-4">
                {BACKGROUNDS.map((bg) => (
                  <Card
                    key={bg.id}
                    className={`relative cursor-pointer overflow-hidden transition-all hover:scale-105 ${
                      selectedBg === bg.id ? 'ring-2 ring-primary' : ''
                    }`}
                    onClick={() => handleSelect(bg.id)}
                  >
                    <div className="aspect-video relative">
                      {bg.type === 'gradient' ? (
                        <div
                          className="w-full h-full"
                          style={{ background: bg.light }}
                        />
                      ) : (
                        <img
                          src={bg.value}
                          alt={bg.name}
                          className="w-full h-full object-cover"
                        />
                      )}
                      {selectedBg === bg.id && (
                        <div className="absolute top-2 right-2 w-6 h-6 bg-primary rounded-full flex items-center justify-center">
                          <Check className="w-4 h-4 text-primary-foreground" />
                        </div>
                      )}
                    </div>
                    <div className="p-3">
                      <p className="text-sm font-medium">{bg.name}</p>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </TabsContent>

          <TabsContent value="appearance" className="space-y-4 mt-4">
            <div>
              <Label className="text-base font-medium">Icon Size</Label>
              <p className="text-sm text-muted-foreground">
                Coming soon...
              </p>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
