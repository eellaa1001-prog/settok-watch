# 셋톡 방 감시: PC가 꺼져 있을 때(5분 넘게 'claude code' 답이 없는 글이 있을 때) 클라우드 루틴을 깨움
# 열쇠·토큰은 GitHub Secrets(SETTOK_KEY, ROUTINE_TOKEN)에서만 읽고, 기록에는 글 번호만 남김
import json, os, re, sys, time, urllib.request

KEY = os.environ["SETTOK_KEY"]
TOKEN = os.environ["ROUTINE_TOKEN"]
FIRE = "https://api.anthropic.com/v1/claude_code/routines/trig_01Je5C1Xw5RG4c8Pnno8JC9c/fire"
ME = "claude code"
CALL = re.compile(r"클로드 코드|claude code|Claude Code")

req = urllib.request.Request(f"https://chat.gonipro.app/api/msgs?k={KEY}&since=0", headers={"User-Agent": "Mozilla/5.0"})
data = json.load(urllib.request.urlopen(req, timeout=30))
now = int(data.get("now") or time.time() * 1000)
msgs = data.get("msgs", [])

pending = []
for m in msgs:
    if m.get("sender_type") != "human":
        continue
    if not (m.get("owner") in (True, "true", "True") or CALL.search(m.get("text", ""))):
        continue
    mid = int(m["id"])
    if any(x.get("who") == ME and int(x["id"]) > mid for x in msgs):
        continue  # 이미 답함
    age = now - int(m["ts"])
    if 5 * 60_000 <= age <= 24 * 3_600_000:
        pending.append(mid)

print("pending:", pending)
if not pending:
    sys.exit(0)

body = json.dumps({"text": f"GitHub 감시: 답 없는 글 {pending}"}).encode()
fire = urllib.request.Request(FIRE, data=body, method="POST", headers={
    "Authorization": f"Bearer {TOKEN}",
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "experimental-cc-routine-2026-04-01",
    "Content-Type": "application/json",
})
print("fire:", urllib.request.urlopen(fire, timeout=30).status)
