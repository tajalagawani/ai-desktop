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
    id: 'image-abstract',
    name: 'Abstract Art',
    type: 'image' as const,
    value: '/backgrounds/abstract-art.jpg'
  },
  {
    id: 'image-blue',
    name: 'Blue Abstract',
    type: 'image' as const,
    value: '/backgrounds/blue-abstract.avif'
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

              <div className="grid grid-cols-3 gap-3">
                {BACKGROUNDS.map((bg) => (
                  <Card
                    key={bg.id}
                    className={`relative cursor-pointer overflow-hidden transition-all hover:scale-105 ${
                      selectedBg === bg.id ? 'ring-2 ring-primary' : ''
                    }`}
                    onClick={() => handleSelect(bg.id)}
                  >
                    <div className="aspect-video relative">
                      <img
                        src={bg.value}
                        alt={bg.name}
                        className="w-full h-full object-cover"
                      />
                      {selectedBg === bg.id && (
                        <div className="absolute top-1 right-1 w-5 h-5 bg-primary rounded-full flex items-center justify-center">
                          <Check className="w-3 h-3 text-primary-foreground" />
                        </div>
                      )}
                    </div>
                    <div className="p-2">
                      <p className="text-xs font-medium">{bg.name}</p>
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
