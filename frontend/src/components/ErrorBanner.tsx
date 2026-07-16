interface Props {
  message: string;
  onDismiss?: () => void;
}

export function ErrorBanner({ message, onDismiss }: Props) {
  return (
    <div className="px-4 py-2 text-red-500 text-sm bg-red-50 border-t border-red-100 flex items-center justify-between gap-2">
      <span>{message}</span>
      {onDismiss && (
        <button
          onClick={onDismiss}
          className="text-red-400 hover:text-red-600 shrink-0"
          aria-label="에러 닫기"
        >
          ✕
        </button>
      )}
    </div>
  );
}
