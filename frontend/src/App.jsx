import { useState } from "react";
import UploadBox from "./components/UploadBox.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import { uploadDocument, extractErrorMessage } from "./api.js";

const HOW_IT_WORKS = [
  { step: "1", title: "Upload", detail: "Drop in a PDF — up to 10MB." },
  { step: "2", title: "Ask", detail: "Ask anything about its contents, in plain English." },
  { step: "3", title: "Get answers", detail: "Grounded in the actual text, with a page citation." },
];

export default function App() {
  const [document, setDocument] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState("");

  async function handleUpload(file) {
    setIsUploading(true);
    setUploadError("");
    try {
      const data = await uploadDocument(file);
      setDocument(data);
    } catch (error) {
      setUploadError(extractErrorMessage(error));
    } finally {
      setIsUploading(false);
    }
  }

  return (
    <div className="min-h-screen px-4 py-10 sm:px-6 sm:py-14">
      <div className="mx-auto max-w-2xl">
        <header className="mb-8 text-center sm:text-left">
          <h1 className="font-serif text-3xl text-ink sm:text-4xl">DocChat</h1>
          <p className="mt-2 font-sans text-sm text-slate sm:text-base">
            Upload a PDF, ask it questions, get answers grounded in the text —
            with the page it came from.
          </p>
        </header>

        {!document ? (
          <>
            <UploadBox onUpload={handleUpload} isUploading={isUploading} />

            {uploadError && (
              <p className="mt-3 rounded-md bg-red-50 px-3 py-2 font-sans text-sm text-red-700">
                {uploadError}
              </p>
            )}

            <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-3">
              {HOW_IT_WORKS.map((item) => (
                <div key={item.step} className="rounded-lg border border-slate/15 bg-white p-4">
                  <span className="font-serif text-sm text-accent">{item.step}</span>
                  <p className="mt-1 font-sans text-sm font-medium text-ink">{item.title}</p>
                  <p className="mt-1 font-sans text-xs text-slate">{item.detail}</p>
                </div>
              ))}
            </div>
          </>
        ) : (
          <>
            <ChatWindow document={document} />
            <button
              onClick={() => setDocument(null)}
              className="mt-3 font-sans text-sm text-slate underline underline-offset-2"
            >
              Upload a different document
            </button>
          </>
        )}
      </div>
    </div>
  );
}
