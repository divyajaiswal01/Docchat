import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE_URL });

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const { data } = await client.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/**
 * Streams an answer via Server-Sent Events.
 * Calls onToken(text) as each piece of the answer arrives, onSources(pages)
 * once retrieval's page numbers are known, onError(message) on failure,
 * and onDone() when the stream finishes normally.
 */
export async function streamAnswer(documentId, question, { onToken, onSources, onError, onDone }) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_id: documentId, question }),
    });
  } catch {
    onError("Couldn't reach the server. Is the backend running?");
    return;
  }

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    onError(data.detail || data.message || "Something went wrong.");
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop(); // last piece may be incomplete — keep it for next read

    for (const raw of events) {
      const line = raw.trim();
      if (!line.startsWith("data:")) continue;

      let event;
      try {
        event = JSON.parse(line.slice(5).trim());
      } catch {
        continue; // skip malformed/partial event
      }

      if (event.type === "token") onToken(event.content);
      else if (event.type === "sources") onSources(event.pages);
      else if (event.type === "error") onError(event.message);
      else if (event.type === "done") onDone(event.remaining_questions);
    }
  }
}

export function extractErrorMessage(error) {
  if (error.response?.data?.detail) return error.response.data.detail;
  if (error.response?.data?.message) return error.response.data.message;
  return "Something went wrong. Please try again.";
}
