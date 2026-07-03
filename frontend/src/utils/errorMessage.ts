// src/utils/errorMessage.ts
export function toUserFriendlyMessage(err: unknown): string {
  // 네트워크 자체가 안 되는 경우 (서버 꺼짐, CORS, 인터넷 끊김 등)
  // 브라우저마다 메시지가 조금씩 다름: "Failed to fetch"(Chrome), "NetworkError"(Firefox) 등
  if (err instanceof TypeError) {
    return "서버에 연결할 수 없어요. 잠시 후 다시 시도해주세요.";
  }

  // AbortController로 30초 후 직접 취소시킨 타임아웃
  if (err instanceof DOMException && err.name === "AbortError") {
    return "응답 시간이 너무 오래 걸려요. 잠시 후 다시 시도해주세요.";
  }

  // 백엔드가 명시적으로 보낸 에러 메시지 (Error 인스턴스로 throw됨)
  if (err instanceof Error) {
    return err.message;
  }

  return "알 수 없는 오류가 발생했어요.";
}
