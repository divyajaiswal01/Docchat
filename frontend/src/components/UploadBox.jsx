import { useRef, useState } from "react";

export default function UploadBox({ onUpload, isUploading }) {
  const inputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  function handleFiles(files) {
    const file = files?.[0];
    if (file) onUpload(file);
  }

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        if (!isUploading) setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragOver(false);
        if (!isUploading) handleFiles(e.dataTransfer.files);
      }}
      onClick={() => !isUploading && inputRef.current?.click()}
      className={`rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors sm:px-8 sm:py-14
        ${isUploading ? "cursor-wait border-slate/20 bg-white" : "cursor-pointer"}
        ${isDragOver ? "border-accent bg-accentLight" : "border-slate/30 bg-white"}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        className="hidden"
        disabled={isUploading}
        onChange={(e) => handleFiles(e.target.files)}
      />
      {isUploading ? (
        <div className="flex flex-col items-center gap-3">
          <div className="h-6 w-6 animate-spin rounded-full border-2 border-slate/20 border-t-accent" />
          <p className="font-sans text-sm text-slate">Reading your document…</p>
        </div>
      ) : (
        <>
          <p className="font-serif text-lg text-ink">Drop a PDF here</p>
          <p className="mt-1 font-sans text-sm text-slate">
            or click to browse — 10MB max
          </p>
        </>
      )}
    </div>
  );
}
