export default function LoadingSkeleton() {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4 animate-pulse">
      {/* User message skeleton */}
      <div className="flex justify-end">
        <div className="w-3/4 h-16 bg-muted/50 rounded-2xl rounded-tr-sm" />
      </div>

      {/* Assistant message skeleton */}
      <div className="flex justify-start">
        <div className="w-4/5 h-24 bg-muted/30 rounded-2xl rounded-tl-sm" />
      </div>

      {/* User message skeleton */}
      <div className="flex justify-end">
        <div className="w-2/3 h-12 bg-muted/50 rounded-2xl rounded-tr-sm" />
      </div>

      {/* Assistant message skeleton */}
      <div className="flex justify-start">
        <div className="w-3/4 h-32 bg-muted/30 rounded-2xl rounded-tl-sm" />
      </div>
    </div>
  );
}
