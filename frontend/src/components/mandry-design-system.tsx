// Mandry Design System
// This file contains the design tokens and styling constants used throughout the application

export const mandryColors = {
  gradients: {
    background: "bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900",
    button: "bg-gradient-to-r from-[#FFF309] to-[#FFF309]/80",
  },
  text: {
    primary: "text-white",
    secondary: "text-gray-300",
    accent: "text-[#FFF309]",
  },
}

export const mandrySpacing = {
  navbar: {
    margin: "pt-20",
  },
  hero: {
    maxWidth: "max-w-7xl",
  },
  button: {
    primary: "px-8 py-3",
  },
}

export const mandryTypography = {
  heading: {
    section: "text-4xl font-bold",
    subsection: "text-2xl font-semibold",
  },
}

export const mandryAnimations = {
  pageEnter: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 },
  },
  textEnter: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6, delay: 0.2 },
  },
  buttonHover: {
    whileHover: { scale: 1.02 },
    whileTap: { scale: 0.98 },
  },
} 