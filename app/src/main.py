import argparse
import re
import urllib

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
from langchain_community.document_loaders import YoutubeLoader

def argparser() -> argparse.ArgumentParser:
  parser = argparse.ArgumentParser(description='YouTubeの文字起こしを取得する')
  parser.add_argument('video_id_url', help='動画ID/URL')
  parser.add_argument(
    "-m", "--mode",
    choices=["youtube-transcript-api", "langchain"],
    default="youtube-transcript-api",
    help="字幕取得エンジンを選択 (youtube-transcript-api: youtube-transcript-api, langchain: LangChain YoutubeLoader)"
  )
  parser.add_argument(
    "-o", "--output",
    type=str,
    default=None,
    help="取得した字幕をテキストファイルとして保存する"
  )
  parser.add_argument(
    "-l", "--language",
    type=str,
    default='ja',
    help="取得する字幕の言語"
  )
  parser.add_argument(
    "-r", "--raw",
    action="store_true",
    default=False,
    help="整形前の字幕を取得する"
  )
  return parser


def clean_text(text: str):
  # 改行を削除
  text = re.sub(r'\n', '', text)
  # 環境音を削除
  text = re.sub(r'\[.*?\]', '', text)
  # スペースを削除
  text = re.sub(r'[ 　]', '', text)

  return text.strip()

def get_transcript_with_youtube_transcript_api(video_id: str, languages: list[str] = ['ja']):
  # 字幕を取得
  ytt_api = YouTubeTranscriptApi()
  fetched_transcript = ytt_api.fetch(video_id, languages=languages)
  # テキストに変換
  formatted_text = TextFormatter().format_transcript(fetched_transcript)

  # for snippet in fetched_transcript:
  #   # snippet.text, snippet.start, snippet.duration
  #   print(snippet.text)

  return formatted_text


def get_transcript_with_langchain(video_id: str, languages: list[str] = ['ja']):
  # 内部的には youtube-transcript-api を使用している
  # デフォルトのフォーマットは TranscriptFormat.TEXT
  loader = YoutubeLoader(
    video_id=video_id,
    language=languages,
  )
  docs = loader.load()
  return docs[0].page_content


if __name__ == "__main__":
  parser = argparser()
  args = parser.parse_args()

  if args.video_id_url.startswith('http'):
    url = urllib.parse.urlparse(args.video_id_url)
    query = urllib.parse.parse_qs(url.query)
    video_id = query.get('v', [None])[0]
    if not video_id:
      raise ValueError(f'URLから動画IDが取得できませんでした。: {args.video_id_url}')
  else:
    video_id = args.video_id_url

  if args.mode == "youtube-transcript-api":
    transcript = get_transcript_with_youtube_transcript_api(video_id, languages=[args.language])
  elif args.mode == "langchain":
    transcript = get_transcript_with_langchain(video_id, languages=[args.language])

  # 整形
  text = transcript if args.raw else clean_text(transcript)

  if args.output:
    with open(args.output, 'w', encoding='utf-8') as file:
      file.write(text)
    print(f'字幕を {args.output} に保存しました。')
  else:
    print(text)