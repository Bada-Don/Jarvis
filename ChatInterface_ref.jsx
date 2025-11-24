import React, { useState, useRef, useEffect } from "react";
import { Paperclip, Send, FileText, Loader2 } from "lucide-react";

// If you use shadcn/ui, you can swap these primitives with <Button>, <Input>, etc.
// The component below is framework-agnostic Tailwind + React and can live inside any app shell.

// Types
interface Attachment {
  id: string;
  name: string;
  size: number;
  url: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  attachments?: Attachment[];
  isStreaming?: boolean;
  progress?: number; // 0-100 for assistant streaming
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};

const createId = () => Math.random().toString(36).slice(2);

export default function AIChatInterface() {
  const [messages, setMessages] = useState<Message[]>([{
    id: createId(),
    role: "assistant",
    content: "Hi, I am your AI assistant. Upload files and send me a message to get started.",
  }]);

  const [input, setInput] = useState("");
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const [isSending, setIsSending] = useState(false);

  const scrollRef = useRef<HTMLDivElement | null>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (!scrollRef.current) return;
    scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages.length]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (!event.target.files) return;
    const filesArray = Array.from(event.target.files);
    setPendingFiles(prev => [...prev, ...filesArray]);
    event.target.value = ""; // reset input so same file can be selected again
  };

  const removePendingFile = (index: number) => {
    setPendingFiles(prev => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      if (!isSending) {
        handleSend();
      }
    }
  };

  const simulateStreamingResponse = (baseText: string, attachments: Attachment[]) => {
    const assistantId = createId();
    const target =
      baseText.trim() === ""
        ? "I have received your message and files. This is a simulated streaming response. Replace this with a real API call."
        : `You said: "${baseText}". This is a simulated streaming reply. Replace this with your real AI backend.`;

    const chunks = target.match(/.{1,12}(\s|$)/g) || [target];

    setMessages(prev => [
      ...prev,
      {
        id: assistantId,
        role: "assistant",
        content: "",
        attachments,
        isStreaming: true,
        progress: 0,
      },
    ]);

    let currentIndex = 0;

    const interval = setInterval(() => {
      currentIndex += 1;

      setMessages(prev => {
        return prev.map(msg => {
          if (msg.id !== assistantId) return msg;
          const nextContent = (msg.content || "") + (chunks[currentIndex - 1] || "");
          const progress = Math.min(100, Math.round((currentIndex / chunks.length) * 100));

          return {
            ...msg,
            content: nextContent,
            progress,
            isStreaming: progress < 100,
          };
        });
      });

      if (currentIndex >= chunks.length) {
        clearInterval(interval);
      }
    }, 80);
  };

  const handleSend = () => {
    const trimmed = input.trim();
    if (!trimmed && pendingFiles.length === 0) return;

    setIsSending(true);

    const attachments: Attachment[] = pendingFiles.map(file => ({
      id: createId(),
      name: file.name,
      size: file.size,
      // Use a local URL for now; in production you would upload to your backend or storage
      url: URL.createObjectURL(file),
    }));

    const userMessage: Message = {
      id: createId(),
      role: "user",
      content: trimmed,
      attachments,
    };

    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setPendingFiles([]);

    // Simulate a streaming AI response. Replace this block with your real API call.
    simulateStreamingResponse(trimmed, []);

    setIsSending(false);
  };

  const renderAttachments = (attachments?: Attachment[]) => {
    if (!attachments || attachments.length === 0) return null;

    return (
      <div className="mt-2 flex flex-col gap-2">
        {attachments.map(att => (
          <a
            key={att.id}
            href={att.url}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-3 rounded-2xl bg-white/10 px-3 py-2 text-xs text-white/90 backdrop-blur-sm hover:bg-white/15"
          >
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/15">
              <FileText className="h-4 w-4" />
            </div>
            <div className="flex flex-1 flex-col overflow-hidden">
              <span className="truncate font-medium">{att.name}</span>
              <span className="text-[10px] text-white/70">{formatFileSize(att.size)}</span>
            </div>
          </a>
        ))}
      </div>
    );
  };

  const renderMessage = (message: Message) => {
    const isUser = message.role === "user";

    return (
      <div
        key={message.id}
        className={`flex w-full gap-2 ${isUser ? "justify-end" : "justify-start"}`}
      >
        {!isUser && (
          <div className="mt-1 h-7 w-7 flex-shrink-0 overflow-hidden rounded-full bg-white/30" />
        )}

        <div className={`max-w-[80%] space-y-1 ${isUser ? "items-end" : "items-start"}`}>
          <div
            className={`rounded-3xl px-4 py-2 text-sm leading-relaxed shadow-sm ${
              isUser
                ? "bg-white text-slate-900"
                : "bg-[#7b5cff] text-white"
            }`}
          >
            <span className="whitespace-pre-wrap break-words">{message.content}</span>
            {renderAttachments(message.attachments)}

            {message.isStreaming && (
              <div className="mt-2 flex items-center gap-2 text-[10px] text-white/80">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>Generating… {message.progress ?? 0}%</span>
              </div>
            )}
          </div>
        </div>

        {isUser && (
          <div className="mt-1 h-7 w-7 flex-shrink-0 overflow-hidden rounded-full bg-white" />
        )}
      </div>
    );
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-b from-slate-100 to-slate-200 px-4 py-6">
      <div className="relative flex h-[720px] w-[360px] max-w-full flex-col rounded-[2.5rem] bg-gradient-to-b from-[#5a3fff] to-[#8f6bff] p-4 shadow-2xl">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between px-1 pt-1">
          <div className="flex items-center gap-3">
            <div className="h-9 w-9 overflow-hidden rounded-full bg-white/90" />
            <div className="flex flex-col">
              <span className="text-sm font-semibold text-white">Aurora AI</span>
              <span className="text-[11px] text-emerald-200">Online · Realtime</span>
            </div>
          </div>
          <div className="flex gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/15">
              <span className="text-xs text-white/80">?</span>
            </div>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-white/15">
              <span className="text-xs text-white/80">i</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div
          ref={scrollRef}
          className="flex-1 space-y-3 overflow-y-auto rounded-3xl bg-white/10 px-3 py-4 backdrop-blur-sm"
        >
          {messages.map(renderMessage)}
        </div>

        {/* Pending attachments preview */}
        {pendingFiles.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2 rounded-2xl bg-white/15 px-3 py-2 text-[11px] text-white/90">
            {pendingFiles.map((file, index) => (
              <div
                key={`${file.name}-${index}`}
                className="flex items-center gap-1 rounded-xl bg-white/15 px-2 py-1"
              >
                <FileText className="h-3 w-3" />
                <span className="max-w-[120px] truncate">{file.name}</span>
                <button
                  type="button"
                  onClick={() => removePendingFile(index)}
                  className="ml-1 text-xs text-white/70 hover:text-white"
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        )}

        {/* Input area */}
        <div className="mt-3 flex items-center gap-2 rounded-full bg-white px-3 py-2 shadow-lg">
          <label className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full bg-slate-100 hover:bg-slate-200">
            <Paperclip className="h-4 w-4" />
            <input
              type="file"
              className="hidden"
              multiple
              onChange={handleFileChange}
            />
          </label>

          <input
            className="flex-1 border-none bg-transparent text-sm text-slate-900 focus:outline-none"
            placeholder="Send a message to the AI…"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
          />

          <button
            type="button"
            onClick={handleSend}
            disabled={isSending || (!input.trim() && pendingFiles.length === 0)}
            className="flex h-9 w-9 items-center justify-center rounded-full bg-[#7b5cff] text-white shadow-md disabled:cursor-not-allowed disabled:bg-slate-300"
          >
            {isSending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </div>
    </div>
  );
}
