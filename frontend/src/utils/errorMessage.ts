export function toUserFriendlyMessage(err: unknown): string {
  if (err instanceof TypeError) {
    return "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.";
  }
  if (err instanceof DOMException && err.name === "AbortError") {
    return "응답 시간이 너무 오래 걸려요. 잠시 후 다시 시도해주세요.";
  }
  if (err instanceof Error) {
    return err.message;
  }
  return "알 수 없는 오류가 발생했어요.";
}
