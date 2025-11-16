# File Manager Refactor Plan - VPS Best Practices

## Current Issues

### 1. **Wrong Default Directory**
- Currently defaults to `/tmp` which shows temporary system folders
- Shows `.font-unix`, `.ICE-unix`, `.X11-unix` etc. (system temp folders)
- Should default to `/var/www` or `/root` for VPS usage

### 2. **Fake Sidebar Data**
- Shows non-existent projects: "Design Engineering", "Sales & Marketing", "Travel"
- Shows fake "Support" and "Feedback" links
- Sidebar should show actual VPS directories

### 3. **Broken Navigation**
- Breadcrumbs don't navigate when clicked
- Folders don't open properly on double-click
- Path resolution is broken

### 4. **No Hidden Files Filter**
- Shows all system files (dotfiles)
- Should have option to hide/show hidden files
- Most VPS file managers hide dotfiles by default

### 5. **Missing Essential Features**
- No file upload
- No file download
- No rename functionality
- No copy/move operations
- No search/filter
- No file preview
- No permissions display

### 6. **Poor UX**
- User profile section is fake data
- Company name "Acme Inc" is placeholder
- No proper error handling
- No loading states

---

## VPS File Manager Best Practices

### 1. **Directory Structure**
```
/var/www          # Web applications (MOST IMPORTANT for VPS)
/root             # Root user home
/home             # User home directories
/etc              # Configuration files (read-only for safety)
/var/log          # System logs
/opt              # Optional software
/srv              # Service data
```

### 2. **Security Considerations**
- **Path Validation**: Prevent directory traversal attacks
- **Permission Checks**: Only show accessible files
- **Whitelist Approach**: Define safe root directories
- **No Symlink Following**: Prevent escaping jail
- **Rate Limiting**: Prevent API abuse
- **File Size Limits**: Prevent large file uploads
- **File Type Whitelist**: Block dangerous file types

### 3. **Essential Features**
1. **Navigation**
   - Breadcrumb navigation
   - Sidebar quick access
   - Back/forward buttons
   - Path bar for direct navigation

2. **File Operations**
   - Create folder
   - Upload file (with progress)
   - Download file
   - Rename file/folder
   - Delete file/folder
   - Copy/Cut/Paste
   - Compress/Extract archives

3. **Viewing**
   - Grid/List/Column views
   - Sort by name/date/size/type
   - Show/hide hidden files
   - File search
   - File preview (images, text, code)

4. **File Details**
   - Size (human readable)
   - Modified date
   - Permissions (rwx format)
   - Owner/Group
   - MIME type

5. **Bulk Operations**
   - Select multiple files
   - Bulk delete
   - Bulk download (zip)
   - Bulk move/copy

---

## Implementation Plan

### Phase 1: Fix Core Navigation (Priority: CRITICAL)
**Goal**: Make file manager actually work for VPS

1. **Update Default Directory**
   - Change `FILE_MANAGER_ROOT` from `/tmp` to `/var/www`
   - Add environment variable `FILE_MANAGER_ROOT=/var/www`
   - Update `.env.example` with proper default

2. **Fix Path Resolution**
   - Fix breadcrumb click navigation
   - Fix folder double-click navigation
   - Handle path normalization properly
   - Add "Back" and "Up One Level" buttons

3. **Replace Fake Sidebar Data**
   - Remove: Projects section (Design Engineering, Sales, Travel)
   - Remove: Secondary nav (Support, Feedback)
   - Replace with real VPS directories:
     ```typescript
     Quick Access:
     - /var/www/ai-desktop (Current App)
     - /var/www (Web Apps)
     - /root (Home)
     - /var/log (Logs)
     - /etc (Config - read-only)
     ```

4. **Add Hidden Files Filter**
   - Add toggle button to show/hide dotfiles
   - Filter files starting with `.` by default
   - Store preference in localStorage

### Phase 2: Essential File Operations (Priority: HIGH)
**Goal**: Add must-have features

1. **File Upload**
   - Drag & drop support
   - File input button
   - Progress indicator
   - Size limit (100MB default)
   - Multiple file upload

2. **File Download**
   - Single file download
   - Folder download (as zip)
   - Bulk download selected files

3. **Rename Operation**
   - Right-click context menu "Rename"
   - Inline editing
   - Validation (no special chars)

4. **Copy/Move Operations**
   - Cut/Copy/Paste buttons
   - Clipboard state management
   - Move between directories
   - Duplicate file/folder

5. **Enhanced Delete**
   - Better confirmation dialog
   - Show what will be deleted
   - Prevent deleting critical system files

### Phase 3: UX Improvements (Priority: MEDIUM)
**Goal**: Better user experience

1. **File Details Panel**
   - Show selected file info in sidebar
   - Display:
     - Full path
     - Size (bytes + human readable)
     - Modified date/time
     - File type
     - Permissions (if available)

2. **Search & Filter**
   - Search bar in header
   - Filter by file type
   - Filter by date range
   - Fuzzy search

3. **View Options**
   - Grid view (current)
   - List view (more details)
   - Column view (multi-pane)
   - View size slider

4. **Loading & Error States**
   - Skeleton loaders
   - Better error messages
   - Retry button
   - Empty state illustrations

5. **Keyboard Shortcuts**
   - `Ctrl/Cmd + C`: Copy
   - `Ctrl/Cmd + V`: Paste
   - `Ctrl/Cmd + X`: Cut
   - `Delete`: Delete selected
   - `F2`: Rename
   - `Ctrl/Cmd + A`: Select all
   - `Escape`: Deselect
   - `Enter`: Open folder/file

### Phase 4: Advanced Features (Priority: LOW)
**Goal**: Pro features

1. **File Preview**
   - Image preview
   - Text/code preview
   - PDF preview
   - Video preview (basic)

2. **Archive Support**
   - Extract .zip, .tar.gz
   - Create archive from selection
   - View archive contents

3. **Permissions Management**
   - Display file permissions
   - Change permissions (chmod)
   - Change owner (chown)

4. **Terminal Integration**
   - "Open in Terminal" button
   - Shows current directory in terminal
   - Run commands on selected files

5. **File Editor**
   - Edit text files inline
   - Syntax highlighting for code
   - Save changes

---

## API Endpoints Design

### Current
- `GET /api/files?path=/` - List files
- `POST /api/files` - Create folder, Delete

### New Structure
```typescript
// List files
GET /api/files?path=/var/www&showHidden=false

// Upload file
POST /api/files/upload
Body: FormData with file(s)

// Download file
GET /api/files/download?path=/var/www/file.txt

// Download folder as zip
GET /api/files/download?path=/var/www/folder&type=folder

// Rename
POST /api/files/rename
Body: { oldPath, newName }

// Copy
POST /api/files/copy
Body: { sourcePath, destPath }

// Move
POST /api/files/move
Body: { sourcePath, destPath }

// Get file info
GET /api/files/info?path=/var/www/file.txt

// Search files
GET /api/files/search?path=/var/www&query=test

// Get disk usage
GET /api/files/disk-usage
```

---

## File Manager State Management

### Recommended Structure
```typescript
interface FileManagerState {
  // Navigation
  currentPath: string
  pathHistory: string[]
  historyIndex: number

  // Files
  files: FileItem[]
  selectedFiles: Set<string>
  clipboard: { items: FileItem[], operation: 'copy' | 'cut' } | null

  // UI State
  viewMode: 'grid' | 'list' | 'columns'
  sortBy: 'name' | 'date' | 'size' | 'type'
  sortOrder: 'asc' | 'desc'
  showHidden: boolean
  sidebarOpen: boolean

  // Loading
  loading: boolean
  error: string | null

  // Operations in progress
  uploading: Map<string, number> // filename -> progress %
  downloading: Set<string>
}
```

---

## Security Implementation

### 1. Path Validation (Current - Good!)
```typescript
// Already implemented correctly
function validatePath(filePath: string): string {
  const absolutePath = path.join(SAFE_ROOT, relativePath)
  if (!absolutePath.startsWith(SAFE_ROOT)) {
    throw new Error('Access denied')
  }
  return absolutePath
}
```

### 2. Additional Security Needed
```typescript
// File upload validation
const ALLOWED_EXTENSIONS = [
  '.jpg', '.png', '.gif', '.pdf', '.txt', '.md',
  '.js', '.ts', '.json', '.html', '.css',
  // ... more safe extensions
]

const MAX_FILE_SIZE = 100 * 1024 * 1024 // 100MB

// Blocked dangerous files
const BLOCKED_EXTENSIONS = [
  '.exe', '.sh', '.bat', '.cmd',  // Executables (except on VPS we might need .sh)
  '.php', '.jsp', '.asp',          // Server scripts
]

// Protected system paths
const PROTECTED_PATHS = [
  '/etc/passwd',
  '/etc/shadow',
  '/etc/sudoers',
  '/root/.ssh',
  // ... more critical paths
]
```

---

## Testing Checklist

### Functional Tests
- [ ] Navigate to /var/www
- [ ] Navigate to /var/www/ai-desktop
- [ ] Create new folder
- [ ] Upload single file
- [ ] Upload multiple files
- [ ] Download file
- [ ] Rename file
- [ ] Delete file
- [ ] Copy file
- [ ] Move file
- [ ] Navigate using breadcrumbs
- [ ] Navigate using sidebar
- [ ] Toggle hidden files
- [ ] Search for files
- [ ] Sort by different columns

### Security Tests
- [ ] Try to access /etc/passwd
- [ ] Try to access /root/.ssh
- [ ] Try path traversal (../)
- [ ] Try symlink following
- [ ] Upload oversized file
- [ ] Upload dangerous file type

### Performance Tests
- [ ] Load directory with 1000+ files
- [ ] Upload 10 files simultaneously
- [ ] Download large file (100MB+)
- [ ] Search in large directory

---

## Quick Wins (Do First!)

1. **Change default directory to /var/www** (5 min)
2. **Remove fake sidebar data** (10 min)
3. **Fix breadcrumb navigation** (15 min)
4. **Add hidden files filter** (20 min)
5. **Fix folder double-click** (10 min)

**Total: ~1 hour to make File Manager actually usable!**

---

## Long-term Improvements

1. **Real-time Updates** - WebSocket for file changes
2. **Collaborative Editing** - Multiple users
3. **Version Control** - File history/snapshots
4. **Cloud Integration** - S3, Dropbox, etc.
5. **File Sharing** - Generate shareable links
6. **Access Control** - User permissions
7. **Audit Log** - Track all file operations
8. **Trash/Recycle Bin** - Soft delete
