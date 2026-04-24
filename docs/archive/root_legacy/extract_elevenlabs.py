import json
import re

transcript_path = '/home/mth/.cursor/projects/OMEGA-CORE/agent-transcripts/8ffb0cfd-4677-43c6-b23b-c77b023691c4/8ffb0cfd-4677-43c6-b23b-c77b023691c4.jsonl'
out_path = '/OMEGA_CORE/frontend/src/components/ElevenLabsBoard.tsx'

found = False
with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            data = json.loads(line)
            if data.get('role') == 'assistant':
                for content in data.get('message', {}).get('content', []):
                    if content.get('type') == 'text':
                        text = content.get('text', '')
                        if '```tsx' in text and ('ElevenLabsBoard' in text or 'GoogleGenAI' in text):
                            matches = re.findall(r'```tsx\n(.*?)```', text, re.DOTALL)
                            for match in matches:
                                if 'ElevenLabsBoard' in match or 'export default function ElevenLabsBoard' in match:
                                    with open(out_path, 'w', encoding='utf-8') as out:
                                        out.write(match)
                                    print('Successfully extracted ElevenLabsBoard.tsx!')
                                    found = True
                                    # keep searching for the latest version in the transcript
        except Exception as e:
            pass

if not found:
    print("Could not find the code block.")
