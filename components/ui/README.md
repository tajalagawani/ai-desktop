# UI Components Inventory

This directory contains reusable UI components based on shadcn/ui.

## Core Components (Always Keep)
- `button.tsx` - Primary button component
- `card.tsx` - Card container
- `dialog.tsx` - Modal dialogs
- `input.tsx` - Text input
- `label.tsx` - Form labels
- `scroll-area.tsx` - Scrollable areas
- `separator.tsx` - Dividers
- `tooltip.tsx` - Tooltips

## Form Components
- `form.tsx` - Form wrapper
- `checkbox.tsx` - Checkboxes
- `radio-group.tsx` - Radio buttons
- `select.tsx` - Dropdowns
- `switch.tsx` - Toggle switches
- `textarea.tsx` - Multiline text
- `input-otp.tsx` - OTP input
- `calendar.tsx` - Date picker
- `slider.tsx` - Range slider

## Layout Components
- `sheet.tsx` - Slide-out panels
- `drawer.tsx` - Bottom drawers
- `tabs.tsx` - Tab navigation
- `accordion.tsx` - Collapsible sections
- `resizable.tsx` - Resizable panels
- `sidebar.tsx` - Side navigation
- `breadcrumb.tsx` - Breadcrumb navigation
- `navigation-menu.tsx` - Navigation menus

## Feedback Components
- `alert.tsx` - Alert messages
- `alert-dialog.tsx` - Alert dialogs
- `toast.tsx` - Toast notifications
- `toaster.tsx` - Toast container
- `sonner.tsx` - Sonner toast provider
- `progress.tsx` - Progress bars
- `skeleton.tsx` - Loading skeletons

## Data Display
- `table.tsx` - Data tables
- `badge.tsx` - Badges
- `avatar.tsx` - User avatars
- `chart.tsx` - Charts
- `pagination.tsx` - Page navigation
- `carousel.tsx` - Image carousel

## Interactive Components
- `dropdown-menu.tsx` - Dropdown menus
- `context-menu.tsx` - Context menus
- `menubar.tsx` - Menu bars
- `command.tsx` - Command palette
- `popover.tsx` - Popovers
- `hover-card.tsx` - Hover cards
- `toggle.tsx` - Toggle buttons
- `toggle-group.tsx` - Toggle button groups
- `collapsible.tsx` - Collapsible content

## Utility Components
- `aspect-ratio.tsx` - Aspect ratio containers

## Custom/Special Components
- `background-beams.tsx` - Animated background
- `text-hover-effect.tsx` - Text animations
- `layout-text-flip.tsx` - Text flip animations
- `apple-cards-carousel.tsx` - Apple-style carousel
- `floating-dock.tsx` - macOS-style dock

## Hooks
- `use-toast.ts` - Toast hook
- `use-mobile.tsx` - Mobile detection hook

## Component Usage Audit

To check if a component is used:
```bash
grep -r "from '@/components/ui/COMPONENT_NAME'" . --include="*.tsx" --include="*.ts"
```

## Maintenance Notes

- Regularly audit unused components
- Keep documentation updated
- Follow shadcn/ui conventions
- Test components before removing
