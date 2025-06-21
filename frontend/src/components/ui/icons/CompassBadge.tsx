import { cn } from '@/lib/utils'

interface CompassBadgeProps {
  className?: string
}

export function CompassBadge({ className }: CompassBadgeProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <svg
        className="w-6 h-6 text-blue-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-1.447-.894L15 4m0 13V4m-6 3l6-3"
        />
      </svg>
      <span className="font-bold text-xl text-gray-900">Mandry AI</span>
    </div>
  )
}
