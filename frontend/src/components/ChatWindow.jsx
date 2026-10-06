import { useState } from "react";
import MessageBubble from "./MessageBubble.jsx";
import { streamAnswer } from "../api.js";

export default function ChatWindow({ document }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [remaining, setRemaining] = useState(null); // null = unknown yet

  function updateLastMessage(updater) {
    setMessages((prev) => {
      const updated = [...prev];
      const last = updated[updated.length - 1];
      updated[updated.length - 1] = { ...last, ...updater(last) };
      return updated;
    });
  }

  const limitReached = remaining === 0;

  async function handleSend() {
    const question = input.trim();
    if (!question || isAsking || limitReached) return;

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
      { role: "assistant", content: "", pages: [] },
    ]);
    setInput("");
    setIsAsking(true);

    await streamAnswer(document.document_id, question, {
      onToken: (token) => {
        updateLastMessage((last) => ({ content: last.content + token }));
      },
      onSources: (pages) => {
        updateLastMessage(() => ({ pages }));
      },
      onError: (message) => {
        updateLastMessage(() => ({ content: message, isError: true }));
      },
      onDone: (remainingQuestions) => {
        if (typeof remainingQuestions === "number") setRemaining(remainingQuestions);
        setIsAsking(false);
      },
    });

    // Safety net: onDone should always fire, but if the stream ends without
    // one (e.g. a network drop), don't leave the UI stuck in "asking" state.
    setIsAsking(false);
  }

  return (
    <div className="flex h-[65vh] sm:h-[70vh] flex-col rounded-lg border border-slate/15 bg-paper">
      <div className="flex items-center justify-between border-b border-slate/15 px-4 py-3 sm:px-5">
        <p className="font-sans text-sm text-slate truncate pr-2">
          {document.filename} · {document.page_count} page
          {document.page_count === 1 ? "" : "s"}
        </p>
        {remaining !== null && (
          <p className={`shrink-0 font-sans text-xs ${remaining <= 3 ? "text-amber-700" : "text-slate"}`}>
            {remaining} question{remaining === 1 ? "" : "s"} left
          </p>
        )}
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto px-4 py-4 sm:px-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <p className="font-sans text-sm text-slate">
              Ask anything about this document to get started.
            </p>
            <p className="mt-1 font-sans text-xs text-slate/70">
              e.g. "What are the key points on page 2?"
            </p>
          </div>
        )}
        {messages.map((m, i) => (
          <MessageBubble
            key={i}
            role={m.role}
            content={m.content}
            pages={m.pages}
            isError={m.isError}
            isStreaming={isAsking && i === messages.length - 1 && m.role === "assistant"}
          />
        ))}
      </div>

      <div className="border-t border-slate/15 p-3">
        {limitReached ? (
          <p className="px-1 font-sans text-sm text-amber-700">
            Question limit reached for this document. Upload it again to keep chatting.
          </p>
        ) : (
          <div className="flex gap-2">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask a question about this document…"
              className="flex-1 rounded-md border border-slate/25 bg-white px-3 py-2 font-sans text-sm text-ink outline-none focus:border-accent"
            />
            <button
              onClick={handleSend}
              disabled={isAsking || !input.trim()}
              className="rounded-md bg-accent px-4 py-2 font-sans text-sm font-medium text-white disabled:opacity-40"
            >
              Ask
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
