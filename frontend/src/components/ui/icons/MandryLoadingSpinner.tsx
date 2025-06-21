import { cn } from '@/lib/utils'

interface MandryLoadingSpinnerProps {
  className?: string
}

export function MandryLoadingSpinner({ className }: MandryLoadingSpinnerProps) {
  return (
    <svg 
        width="128" 
        height="128" 
        viewBox="0 0 128 128" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
        className={cn('animate-spin', className)}
    >
        <g clip-path="url(#clip0_26_75)">
        <path d="M63.3661 59.3195L63.4814 59.4196L63.5967 59.3195L93.7924 32.9991L67.4727 63.1954L67.3725 63.3108L67.4727 63.4261L94.052 93.8448L63.634 67.2648L63.5187 67.1646L63.4033 67.2648L33.2063 93.5851L59.5274 63.3888L59.6275 63.2735L59.5274 63.1581L32.9466 32.7394L63.3661 59.3195Z" fill="url(#paint0_radial_26_75)" stroke="#FFF309" strokeWidth="0.350226"/>
        <path d="M68.835 57.7412L68.8535 57.8701L68.9834 57.8887L106.509 63.3613L68.9834 68.835L68.8535 68.8535L68.835 68.9834L63.3613 106.509L57.8887 68.9834L57.8701 68.8535L57.7412 68.835L20.2139 63.3613L57.7412 57.8887L57.8701 57.8701L57.8887 57.7412L63.3613 20.2139L68.835 57.7412Z" fill="url(#paint1_radial_26_75)" stroke="#FFF309" strokeWidth="0.350226"/>
        </g>
        <defs>
        <radialGradient id="paint0_radial_26_75" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(63.5 63.2919) rotate(45) scale(45.8148 45.402)">
        <stop offset="0.495192" stop-color="#FFF309"/>
        <stop offset="0.788462" stop-color="white"/>
        </radialGradient>
        <radialGradient id="paint1_radial_26_75" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(63.362 63.362) rotate(90) scale(44.362)">
        <stop stop-color="white"/>
        <stop offset="0.427885" stop-color="#FFF309"/>
        </radialGradient>
        <clipPath id="clip0_26_75">
        <rect width="128" height="128" rx="19" fill="white"/>
        </clipPath>
        </defs>
    </svg>
  )
} 