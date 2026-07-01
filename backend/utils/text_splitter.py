from langchain_text_splitters import RecursiveCharacterTextSplitter

def get_optimal_chunk_size(file_path: str, margin: int = 50, seperator: str = "\n\n"):
  """
  텍스트 파일을 Q&A 단위로 분할했을 때,
  가장 긴 단락이 잘리지 않도록 최적의 chunk_size를 계산하는 함수

  Args:
    file_path (str): 분할할 텍스트 파일 경로
    margin (int): 안전 마진(기본값 50자) - 가장 긴 단락 길이에 추가할 여유분
    separator (str): Q&A 쌍을 구분하는 기준 문자열 (기본값 "\n\n")

  Returns:
    int: 계산된 optimal_chunk_size
  """
  
  # 1. 파일 읽기
  with open(file_path, "r", encoding="utf-8") as file:
    manual_text = file.read()

  # 2. 구분자 기준으로 Q&A 쌍 분할 (빈 문자열 제거)
  qa_pairs = [pair for pair in manual_text.split(seperator) if pair.strip()]

  # 3. 각 Q&A 쌍의 글자 수 계산
  character_length = [len(pair) for pair in qa_pairs]

  # 4. 가장 긴 Q&A 쌍의 글자 수 추출
  max_char_length = max(character_length)

  # 5. 안전 마진을 더해 최종 chunk_size 결정
  optimal_chunk_size = max_char_length + margin

  return optimal_chunk_size


# 사용 예시
if __name__ == "__main__":
  chunk_size = get_optimal_chunk_size(
    file_path='/Users/leechaejun/selfstudy-repo/lectures/agent/data/manual.txt'
  )
  print(f"설정할 최적의 chunk_size: {chunk_size}자")

  # 이렇게 다른 곳에서 바로 활용 가능
  text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=0)