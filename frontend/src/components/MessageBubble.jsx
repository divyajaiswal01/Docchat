import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// Maps Markdown elements to Tailwind-styled versions that fit the chat
// bubble's spacing — without this, react-markdown's default output (extra
// margins, unstyled tables) looks out of place inside a narrow bubble.
const markdownComponents = {
  p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
  strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
  ul: ({ children }) => <ul className="mb-2 ml-4 list-disc space-y-0.5 last:mb-0">{children}</ul>,
  ol: ({ children }) => <ol className="mb-2 ml-4 list-decimal space-y-0.5 last:mb-0">{children}</ol>,
  li: ({ children }) => <li>{children}</li>,
  code: ({ children }) => (
    <code className="rounded bg-ink/5 px-1 py-0.5 font-mono text-[13px]">{children}</code>
  ),
  a: ({ children, href }) => (
    <a href={href} target="_blank" rel="noopener noreferrer" className="underline text-accent">
      {children}
    </a>
  ),
  table: ({ children }) => (
    <div className="mb-2 overflow-x-auto last:mb-0">
      <table className="min-w-full border-collapse text-[13px]">{children}</table>
    </div>
  ),
  thead: ({ children }) => <thead className="bg-ink/5">{children}</thead>,
  th: ({ children }) => (
    <th className="border border-slate/20 px-2 py-1 text-left font-semibold">{children}</th>
  ),
  td: ({ children }) => <td className="border border-slate/20 px-2 py-1 align-top">{children}</td>,
};

export default function MessageBubble({ role, content, pages, isError, isStreaming }) {
  const isUser = role === "user";
  const isWaitingForFirstToken = isStreaming && content === "";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="max-w-[85%] sm:max-w-[75%]">
        <div
          className={`rounded-lg px-4 py-2.5 font-sans text-[15px] leading-relaxed
            ${isUser ? "bg-accent text-white" : "bg-white text-ink border border-slate/15"}
            ${isError ? "border-red-300 bg-red-50 text-red-800" : ""}`}
        >
          {isWaitingForFirstToken ? (
            <span className="text-slate">Thinking…</span>
          ) : isUser || isError ? (
            // User messages and error text stay plain — no need to parse
            // Markdown from a question the person typed themselves, and
            // error strings are always plain sentences.
            content
          ) : (
            <>
              <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
                {content}
              </ReactMarkdown>
              {isStreaming && (
                <span className="inline-block w-1.5 h-4 ml-0.5 bg-accent/60 animate-pulse align-text-bottom" />
              )}
            </>
          )}
        </div>

        {!isUser && !isError && pages && pages.length > 0 && (
          <p className="mt-1 px-1 font-sans text-xs text-slate">
            Source: {pages.length === 1 ? "page" : "pages"} {pages.join(", ")}
          </p>
        )}
      </div>
    </div>
  );
}
