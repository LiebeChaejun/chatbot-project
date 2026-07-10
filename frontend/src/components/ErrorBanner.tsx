interface Props {
  message: string;
}

export function ErrorBanner({ message }: Props) {
  return (
    <div className="px-4 py-2 text-red-500 text-sm bg-red-50 border-t border-red-100">
      {message}
    </div>
  );
}
