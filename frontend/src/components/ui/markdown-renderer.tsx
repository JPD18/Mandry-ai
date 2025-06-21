import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  // Transform citation references [Source X] into clickable components
  const transformCitations = (text: string) => {
    return text.replace(/\[Source (\d+)\]/g, (_, sourceNumber) => {
      return `<sup id="ref-${sourceNumber}" class="citation-ref"><a href="#cite-${sourceNumber}" class="text-blue-600 hover:text-blue-800">[${sourceNumber}]</a></sup>`
    })
  }

  const transformed = transformCitations(content)

  const components = {
    // Custom rendering for different markdown elements
    p: ({ children, ...props }: any) => (
      <p className="mb-3 leading-relaxed text-white" {...props}>
        {children}
      </p>
    ),
    strong: ({ children, ...props }: any) => (
      <strong className="font-semibold text-white" {...props}>
        {children}
      </strong>
    ),
    em: ({ children, ...props }: any) => (
      <em className="italic text-white" {...props}>
        {children}
      </em>
    ),
    ul: ({ children, ...props }: any) => (
      <ul className="list-disc list-inside mb-3 space-y-1 text-white" {...props}>
        {children}
      </ul>
    ),
    ol: ({ children, ...props }: any) => (
      <ol className="list-decimal list-inside mb-3 space-y-1 text-white" {...props}>
        {children}
      </ol>
    ),
    li: ({ children, ...props }: any) => (
      <li className="text-white" {...props}>
        {children}
      </li>
    ),
    a: ({ children, href, ...props }: any) => (
      <a
        href={href}
        className="text-blue-300 hover:text-blue-500 underline"
        target="_blank"
        rel="noopener noreferrer"
        {...props}
      >
        {children}
      </a>
    ),
    blockquote: ({ children, ...props }: any) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 italic text-white mb-3" {...props}>
        {children}
      </blockquote>
    ),
    code: ({ children, ...props }: any) => (
      <code className="bg-white/10 px-1 py-0.5 rounded text-sm font-mono text-yellow-200" {...props}>
        {children}
      </code>
    ),
    pre: ({ children, ...props }: any) => (
      <pre className="bg-white/10 p-3 rounded-lg overflow-x-auto text-sm font-mono mb-3 text-white" {...props}>
        {children}
      </pre>
    ),
  }

  return (
    <div className={`prose prose-sm prose-invert max-w-none ${className}`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
        components={components}
      >
        {transformed}
      </ReactMarkdown>
    </div>
  )
} 