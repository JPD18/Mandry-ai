"use client"

import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MandryBaseIcon } from "./mandry-icon"
import { Navbar } from "./Navbar"

export default function AboutUsPage() {
  const [activeSection, setActiveSection] = useState("overview")

  const sections = [
    { id: "overview", label: "Overview", icon: "🧭" },
    { id: "values", label: "Values", icon: "⭐" },
    { id: "mission", label: "Mission", icon: "🎯" },
    { id: "functionality", label: "Features", icon: "⚡" },
  ]

  return (
    <div className="h-screen overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800">
      {/* Font loading */}
      <style jsx global>{`
        @import url('https://fonts.googleapis.com/css2?family=Misto:wght@400;500;600;700&display=swap');
        
        .misto-font {
          font-family: 'Misto', sans-serif;
        }
      `}</style>

      <Navbar 
        showAboutUs={true}
        showChat={true}
        showSchedule={true}
      />

      <div className="pt-20 h-full flex flex-col">
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex-1 px-6 py-12"
        >
          <div className="max-w-7xl mx-auto">
            {/* About Us Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.6 }}
              className="text-center mb-12"
            >
              <h1 className="text-5xl font-bold text-white mb-4 misto-font">About Us</h1>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                Discover who we are, what we stand for, and how we're revolutionizing digital navigation
              </p>
            </motion.div>

            {/* Section Navigation */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.6 }}
              className="flex justify-center mb-12"
            >
              <div className="bg-white/10 backdrop-blur-sm rounded-2xl border border-white/20 p-2 flex space-x-2">
                {sections.map((section, index) => (
                  <motion.button
                    key={section.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 + index * 0.1, duration: 0.4 }}
                    onClick={() => setActiveSection(section.id)}
                    className={`flex items-center space-x-2 px-6 py-3 rounded-xl transition-all duration-300 ${
                      activeSection === section.id
                        ? "bg-yellow-500/30 text-yellow-300 shadow-lg"
                        : "text-gray-300 hover:text-white hover:bg-white/10"
                    }`}
                  >
                    <span className="text-lg">{section.icon}</span>
                    <span className="font-medium">{section.label}</span>
                  </motion.button>
                ))}
              </div>
            </motion.div>

            {/* Content Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6, duration: 0.6 }}
              className="bg-white/5 backdrop-blur-sm rounded-2xl border border-white/10 p-8 min-h-[600px]"
            >
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeSection}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.4 }}
                >
                  {activeSection === "overview" && <OverviewSection />}
                  {activeSection === "values" && <ValuesSection />}
                  {activeSection === "mission" && <MissionSection />}
                  {activeSection === "functionality" && <FunctionalitySection />}
                </motion.div>
              </AnimatePresence>
            </motion.div>
          </div>
        </motion.section>
      </div>
    </div>
  )
}

function OverviewSection() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {[
        {
          title: "Navigate",
          description:
            "Find your way through complex digital landscapes with intuitive guidance and smart pathfinding.",
          icon: "🧭",
          color: "from-blue-500/20 to-cyan-500/20 border-blue-400/30",
        },
        {
          title: "Explore",
          description: "Discover new territories and opportunities with powerful exploration tools and insights.",
          icon: "🗺️",
          color: "from-green-500/20 to-emerald-500/20 border-green-400/30",
        },
        {
          title: "Adventure",
          description: "Embark on exciting digital expeditions with confidence and comprehensive support.",
          icon: "⛰️",
          color: "from-purple-500/20 to-pink-500/20 border-purple-400/30",
        },
      ].map((feature, index) => (
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1, duration: 0.6 }}
          whileHover={{ scale: 1.05, y: -5 }}
          className={`bg-gradient-to-br ${feature.color} backdrop-blur-sm rounded-xl border p-8 hover:shadow-2xl transition-all duration-300`}
        >
          <div className="text-4xl mb-4">{feature.icon}</div>
          <h3 className="text-2xl font-bold text-white mb-4">{feature.title}</h3>
          <p className="text-gray-300 leading-relaxed">{feature.description}</p>
        </motion.div>
      ))}
    </div>
  )
}

function ValuesSection() {
  const values = [
    {
      title: "Precision",
      description: "Every detail matters. We deliver accurate, reliable solutions that you can depend on.",
      icon: "🎯",
    },
    {
      title: "Innovation",
      description: "Pushing boundaries with cutting-edge technology and creative problem-solving approaches.",
      icon: "💡",
    },
    {
      title: "Accessibility",
      description: "Making powerful tools available to everyone, regardless of technical expertise.",
      icon: "🌍",
    },
    {
      title: "Trust",
      description: "Building lasting relationships through transparency, reliability, and consistent excellence.",
      icon: "🤝",
    },
  ]

  return (
    <div className="space-y-8">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">Our Core Values</h2>
        <p className="text-xl text-gray-300">The principles that guide everything we do</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {values.map((value, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, x: index % 2 === 0 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1, duration: 0.6 }}
            className="bg-white/10 backdrop-blur-sm rounded-xl border border-white/20 p-6 hover:bg-white/15 transition-all duration-300"
          >
            <div className="flex items-start space-x-4">
              <div className="text-3xl">{value.icon}</div>
              <div>
                <h3 className="text-xl font-bold text-white mb-2">{value.title}</h3>
                <p className="text-gray-300">{value.description}</p>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function MissionSection() {
  return (
    <div className="text-center space-y-12">
      <div>
        <h2 className="text-4xl font-bold text-white mb-6">Our Mission</h2>
        <div className="bg-gradient-to-r from-yellow-500/20 to-yellow-300/20 backdrop-blur-sm rounded-2xl border border-yellow-400/30 p-12">
          <p className="text-2xl text-white leading-relaxed mb-8">
            "To empower individuals and organizations with intuitive digital navigation tools that transform complex
            challenges into clear, actionable pathways."
          </p>
          <div className="flex justify-center">
            <MandryBaseIcon size={60} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12">
        {[
          {
            title: "Simplify Complexity",
            description: "Transform overwhelming digital landscapes into manageable, navigable experiences.",
            icon: "🔄",
          },
          {
            title: "Enable Growth",
            description: "Provide tools and insights that help users and businesses reach their full potential.",
            icon: "📈",
          },
          {
            title: "Foster Connection",
            description: "Bridge gaps between technology and human needs through thoughtful design.",
            icon: "🌐",
          },
        ].map((goal, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.2, duration: 0.6 }}
            className="bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-6 text-center"
          >
            <div className="text-3xl mb-4">{goal.icon}</div>
            <h3 className="text-lg font-semibold text-white mb-3">{goal.title}</h3>
            <p className="text-gray-300 text-sm">{goal.description}</p>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

function FunctionalitySection() {
  const features = [
    {
      category: "Navigation Tools",
      items: [
        "Smart pathfinding algorithms",
        "Real-time route optimization",
        "Interactive mapping interface",
        "Waypoint management system",
      ],
      icon: "🧭",
      color: "from-blue-500/10 to-blue-600/10 border-blue-400/20",
    },
    {
      category: "Analytics & Insights",
      items: [
        "Performance tracking dashboard",
        "Predictive analytics engine",
        "Custom reporting tools",
        "Data visualization suite",
      ],
      icon: "📊",
      color: "from-green-500/10 to-green-600/10 border-green-400/20",
    },
    {
      category: "Collaboration Features",
      items: [
        "Team workspace management",
        "Real-time collaboration tools",
        "Shared project templates",
        "Communication integrations",
      ],
      icon: "👥",
      color: "from-purple-500/10 to-purple-600/10 border-purple-400/20",
    },
    {
      category: "Customization Options",
      items: [
        "Personalized user interfaces",
        "Custom workflow builders",
        "API integration capabilities",
        "Theme and layout options",
      ],
      icon: "⚙️",
      color: "from-orange-500/10 to-orange-600/10 border-orange-400/20",
    },
  ]

  return (
    <div className="space-y-8">
      <div className="text-center mb-12">
        <h2 className="text-4xl font-bold text-white mb-4">Core Functionality</h2>
        <p className="text-xl text-gray-300">Powerful features designed to enhance your digital journey</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {features.map((feature, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.6 }}
            className={`bg-gradient-to-br ${feature.color} backdrop-blur-sm rounded-xl border p-6`}
          >
            <div className="flex items-center space-x-3 mb-6">
              <div className="text-2xl">{feature.icon}</div>
              <h3 className="text-xl font-bold text-white">{feature.category}</h3>
            </div>

            <ul className="space-y-3">
              {feature.items.map((item, itemIndex) => (
                <motion.li
                  key={itemIndex}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 + itemIndex * 0.05, duration: 0.4 }}
                  className="flex items-center space-x-3 text-gray-300"
                >
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  <span>{item}</span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </div>
  )
} 