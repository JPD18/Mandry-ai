interface IconProps {
  size?: number
  className?: string
}

export function MandryBaseIcon({ size = 24, className = "" }: IconProps) {
  return (
    <div className={`inline-block ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="63.5294" cy="63.7375" r="45.2376" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.58371" />

        {/* All the compass segments */}
        <mask id="path-3-inside-1_26_61" fill="white">
          <path d="M22.5964 37.7943C26.5129 31.6063 31.7667 26.375 37.9712 22.4849L64 64L22.5964 37.7943Z" />
        </mask>
        <path
          d="M22.5964 37.7943C26.5129 31.6063 31.7667 26.375 37.9712 22.4849L64 64L22.5964 37.7943Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-3-inside-1_26_61)"
        />

        <mask id="path-4-inside-2_26_61" fill="white">
          <path d="M105.404 37.7943C101.487 31.6063 96.2333 26.375 90.0288 22.4849L64 64L105.404 37.7943Z" />
        </mask>
        <path
          d="M105.404 37.7943C101.487 31.6063 96.2333 26.375 90.0288 22.4849L64 64L105.404 37.7943Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-4-inside-2_26_61)"
        />

        <mask id="path-5-inside-3_26_61" fill="white">
          <path d="M111.849 74.558C113.427 67.4068 113.382 59.9928 111.717 52.8613L64 64L111.849 74.558Z" />
        </mask>
        <path
          d="M111.849 74.558C113.427 67.4068 113.382 59.9928 111.717 52.8613L64 64L111.849 74.558Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-5-inside-3_26_61)"
        />

        <mask id="path-6-inside-4_26_61" fill="white">
          <path d="M16.151 74.558C14.573 67.4068 14.6181 59.9928 16.2828 52.8613L64 64L16.151 74.558Z" />
        </mask>
        <path
          d="M16.151 74.558C14.573 67.4068 14.6181 59.9928 16.2828 52.8613L64 64L16.151 74.558Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-6-inside-4_26_61)"
        />

        <mask id="path-7-inside-5_26_61" fill="white">
          <path d="M52.217 16.4378C59.3253 14.6768 66.738 14.5315 73.9099 16.0126L64 64L52.217 16.4378Z" />
        </mask>
        <path
          d="M52.217 16.4378C59.3253 14.6768 66.738 14.5315 73.9099 16.0126L64 64L52.217 16.4378Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-7-inside-5_26_61)"
        />

        <mask id="path-8-inside-6_26_61" fill="white">
          <path d="M52.217 111.562C59.3253 113.323 66.738 113.469 73.9099 111.987L64 64L52.217 111.562Z" />
        </mask>
        <path
          d="M52.217 111.562C59.3253 113.323 66.738 113.469 73.9099 111.987L64 64L52.217 111.562Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-8-inside-6_26_61)"
        />

        <mask id="path-9-inside-7_26_61" fill="white">
          <path d="M22.5964 90.2057C26.5129 96.3937 31.7667 101.625 37.9712 105.515L64 64L22.5964 90.2057Z" />
        </mask>
        <path
          d="M22.5964 90.2057C26.5129 96.3937 31.7667 101.625 37.9712 105.515L64 64L22.5964 90.2057Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-9-inside-7_26_61)"
        />

        <mask id="path-10-inside-8_26_61" fill="white">
          <path d="M105.404 90.2057C101.487 96.3937 96.2333 101.625 90.0288 105.515L64 64L105.404 90.2057Z" />
        </mask>
        <path
          d="M105.404 90.2057C101.487 96.3937 96.2333 101.625 90.0288 105.515L64 64L105.404 90.2057Z"
          fill="#31B8E9"
          stroke="#FFF309"
          strokeWidth="1.16742"
          mask="url(#path-10-inside-8_26_61)"
        />

        {/* Inner circles */}
        <circle cx="63.6878" cy="63.8959" r="32.3959" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.58371" />
        <circle cx="64.1878" cy="64.1878" r="26.945" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.485496" />
      </svg>
    </div>
  )
}

export function MandryStarIcon({ size = 24, className = "", uniqueId }: IconProps & { uniqueId?: string }) {
  const paint0 = `paint0_radial_${uniqueId || 'default'}`;
  const paint1 = `paint1_radial_${uniqueId || 'default'}`;
  const clip0 = `clip0_${uniqueId || 'default'}`;

  return (
    <div className={`inline-block ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g clipPath={`url(#${clip0})`}>
          <path
            d="M63.3661 59.5276L63.4814 59.6277L63.5967 59.5276L93.7924 33.2072L67.4727 63.4036L67.3725 63.5189L67.4727 63.6342L94.052 94.0529L63.634 67.4729L63.5187 67.3727L63.4033 67.4729L33.2063 93.7933L59.5274 63.5969L59.6275 63.4816L59.5274 63.3663L32.9466 32.9476L63.3661 59.5276Z"
            fill={`url(#${paint0})`}
            stroke="#FFF309"
            strokeWidth="0.350226"
          />
          <path
            d="M68.835 57.9493L68.8535 58.0782L68.9834 58.0968L106.509 63.5695L68.9834 69.0431L68.8535 69.0616L68.835 69.1915L63.3613 106.717L57.8887 69.1915L57.8701 69.0616L57.7412 69.0431L20.2139 63.5695L57.7412 58.0968L57.8701 58.0782L57.8887 57.9493L63.3613 20.422L68.835 57.9493Z"
            fill={`url(#${paint1})`}
            stroke="#FFF309"
            strokeWidth="0.350226"
          />
        </g>
        <defs>
          <radialGradient
            id={paint0}
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(63.5 63.5) rotate(45) scale(45.8148 45.402)"
          >
            <stop offset="0.495192" stopColor="#FFF309" />
            <stop offset="0.788462" stopColor="white" />
          </radialGradient>
          <radialGradient
            id={paint1}
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(63.362 63.5701) rotate(90) scale(44.362)"
          >
            <stop stopColor="white" />
            <stop offset="0.427885" stopColor="#FFF309" />
          </radialGradient>
          <clipPath id={clip0}>
            <rect width="128" height="128" rx="19" fill="white" />
          </clipPath>
        </defs>
      </svg>
    </div>
  )
}

export function MandryMainIconCyan({ size = 24, className = "" }: IconProps) {
  return (
    <div className={`inline-block ${className}`} style={{ width: size, height: size }}>
      <svg width={size} height={size} viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g clipPath="url(#clip0_20_26)">
          <circle cx="63.5294" cy="63.7375" r="45.2376" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.58371" />

          {/* All the compass segments */}
          <mask id="path-3-inside-1_20_26" fill="white">
            <path d="M22.5964 37.7943C26.5129 31.6063 31.7667 26.375 37.9712 22.4849L64 64L22.5964 37.7943Z" />
          </mask>
          <path
            d="M22.5964 37.7943C26.5129 31.6063 31.7667 26.375 37.9712 22.4849L64 64L22.5964 37.7943Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-3-inside-1_20_26)"
          />

          <mask id="path-4-inside-2_20_26" fill="white">
            <path d="M105.404 37.7943C101.487 31.6063 96.2333 26.375 90.0288 22.4849L64 64L105.404 37.7943Z" />
          </mask>
          <path
            d="M105.404 37.7943C101.487 31.6063 96.2333 26.375 90.0288 22.4849L64 64L105.404 37.7943Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-4-inside-2_20_26)"
          />

          <mask id="path-5-inside-3_20_26" fill="white">
            <path d="M111.849 74.558C113.427 67.4068 113.382 59.9928 111.717 52.8613L64 64L111.849 74.558Z" />
          </mask>
          <path
            d="M111.849 74.558C113.427 67.4068 113.382 59.9928 111.717 52.8613L64 64L111.849 74.558Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-5-inside-3_20_26)"
          />

          <mask id="path-6-inside-4_20_26" fill="white">
            <path d="M16.151 74.558C14.573 67.4068 14.6181 59.9928 16.2828 52.8613L64 64L16.151 74.558Z" />
          </mask>
          <path
            d="M16.151 74.558C14.573 67.4068 14.6181 59.9928 16.2828 52.8613L64 64L16.151 74.558Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-6-inside-4_20_26)"
          />

          <mask id="path-7-inside-5_20_26" fill="white">
            <path d="M52.217 16.4378C59.3253 14.6768 66.738 14.5315 73.9099 16.0126L64 64L52.217 16.4378Z" />
          </mask>
          <path
            d="M52.217 16.4378C59.3253 14.6768 66.738 14.5315 73.9099 16.0126L64 64L52.217 16.4378Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-7-inside-5_20_26)"
          />

          <mask id="path-8-inside-6_20_26" fill="white">
            <path d="M52.217 111.562C59.3253 113.323 66.738 113.469 73.9099 111.987L64 64L52.217 111.562Z" />
          </mask>
          <path
            d="M52.217 111.562C59.3253 113.323 66.738 113.469 73.9099 111.987L64 64L52.217 111.562Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-8-inside-6_20_26)"
          />

          <mask id="path-9-inside-7_20_26" fill="white">
            <path d="M22.5964 90.2057C26.5129 96.3937 31.7667 101.625 37.9712 105.515L64 64L22.5964 90.2057Z" />
          </mask>
          <path
            d="M22.5964 90.2057C26.5129 96.3937 31.7667 101.625 37.9712 105.515L64 64L22.5964 90.2057Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-9-inside-7_20_26)"
          />

          <mask id="path-10-inside-8_20_26" fill="white">
            <path d="M105.404 90.2057C101.487 96.3937 96.2333 101.625 90.0288 105.515L64 64L105.404 90.2057Z" />
          </mask>
          <path
            d="M105.404 90.2057C101.487 96.3937 96.2333 101.625 90.0288 105.515L64 64L105.404 90.2057Z"
            fill="#31B8E9"
            stroke="#FFF309"
            strokeWidth="1.16742"
            mask="url(#path-10-inside-8_20_26)"
          />

          {/* Inner circles */}
          <circle cx="63.6878" cy="63.8959" r="32.3959" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.58371" />
          <circle cx="64.1878" cy="64.1878" r="26.945" fill="#31B8E9" stroke="#FFF309" strokeWidth="0.485496" />

          {/* Star patterns - these are part of the complete logo */}
          <path
            d="M63.3661 59.5276L63.4814 59.6277L63.5967 59.5276L93.7924 33.2072L67.4727 63.4036L67.3725 63.5189L67.4727 63.6342L94.052 94.0529L63.634 67.4729L63.5187 67.3727L63.4033 67.4729L33.2063 93.7933L59.5274 63.5969L59.6275 63.4816L59.5274 63.3663L32.9466 32.9476L63.3661 59.5276Z"
            fill="url(#paint0_radial_20_26)"
            stroke="#FFF309"
            strokeWidth="0.350226"
          />
          <path
            d="M68.835 57.9493L68.8535 58.0782L68.9834 58.0968L106.509 63.5695L68.9834 69.0431L68.8535 69.0616L68.835 69.1915L63.3613 106.717L57.8887 69.1915L57.8701 69.0616L57.7412 69.0431L20.2139 63.5695L57.7412 58.0968L57.8701 58.0782L57.8887 57.9493L63.3613 20.422L68.835 57.9493Z"
            fill="url(#paint1_radial_20_26)"
            stroke="#FFF309"
            strokeWidth="0.350226"
          />
        </g>
        <defs>
          <radialGradient
            id="paint0_radial_20_26"
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(63.5 63.5) rotate(45) scale(45.8148 45.402)"
          >
            <stop offset="0.495192" stopColor="#FFF309" />
            <stop offset="0.788462" stopColor="white" />
          </radialGradient>
          <radialGradient
            id="paint1_radial_20_26"
            cx="0"
            cy="0"
            r="1"
            gradientUnits="userSpaceOnUse"
            gradientTransform="translate(63.362 63.5701) rotate(90) scale(44.362)"
          >
            <stop stopColor="white" />
            <stop offset="0.427885" stopColor="#FFF309" />
          </radialGradient>
          <clipPath id="clip0_20_26">
            <rect width="128" height="128" rx="19" fill="white" />
          </clipPath>
        </defs>
      </svg>
    </div>
  )
} 