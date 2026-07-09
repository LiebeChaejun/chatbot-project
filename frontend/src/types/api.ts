export type ChatApiResponse =
  | { response: string; error?: never }
  | { error: string; response?: never };
