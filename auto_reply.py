import time
import requests
import pyperclip
import subprocess
import win32gui


# ============ Config ============
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL = "deepseek-r1-distill-qwen-14b"
SKILL_DIR = r"F:\skill"
THINK_OPEN = "&lt;think&gt;"
THINK_CLOSE = "&lt;/think&gt;"
MAX_HISTORY = 6
# ==============================




def load_skill():
    persona = ""
    work = ""
    try:
        with open(SKILL_DIR + "\\persona.md", "r", encoding="utf-8") as f:
            persona = f.read()
        with open(SKILL_DIR + "\\work.md", "r", encoding="utf-8") as f:
            work = f.read()
    except Exception:
        print("Skill File not found")
    return (
        "You are a family member chatting on WeChat. "
            "Reply in 15 words or less, colloquial and caring. "
            "Never make things up. "
            "Persona: " + persona + " Style: " + work
    )




def clean_reply(text):
    # Use string search to remove think blocks without regular expressions
    result = text
    while True:
        start = result.find(THINK_OPEN)
        if start == -1:
            break
        end = result.find(THINK_CLOSE, start)
        if end == -1:
            # The think block is unclosed and truncated, discard all subsequent content
            result = result[:start]
            break
        result = result[:start] + result[end + len(THINK_CLOSE):]


    result = result.strip()
    if "\n" in result:
        result = result.split("\n")[0].strip()
    return result




def get_reply(system_prompt, message, history):
    try:
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(history[-(MAX_HISTORY * 2):])
        messages.append({"role": "user", "content": "Family member said:" + message})


        resp = requests.post(LM_STUDIO_URL, json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": 512,
            "temperature": 0.7,
            "stream": False
        }, timeout=60)


        msg = resp.json()["choices"][0]["message"]
        text = msg.get("content", "")


        if not text or text.strip() == "":
            text = msg.get("reasoning_content", "")


        cleaned = clean_reply(text)
        if not cleaned:
            print("[Debug] Empty after cleaning, original:", repr(text[:200]))
            return None
        return cleaned


    except Exception as e:
        print("API error:", e)
        return None




def read_messages():
    from pywinauto import Desktop
    try:
        w = Desktop(backend="uia").window(title="微信")
        texts = []
        for desc in w.descendants():
            try:
                t = desc.window_text()
                cls = desc.class_name()
                if t and 2 < len(t) < 300 and ("Text" in str(cls) or "Msg" in str(cls)):
                    texts.append(t)
            except Exception:
                continue
        return texts
    except Exception:
        return []




def send_message(text):
    hwnd = win32gui.FindWindow(None, "微信")
    if hwnd:
        win32gui.SetForegroundWindow(hwnd)
    time.sleep(0.3)
    pyperclip.copy(text)
    time.sleep(0.1)
    cmd = "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('^v')"
    subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    time.sleep(0.3)
    cmd2 = "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{ENTER}')"
    subprocess.run(["powershell", "-Command", cmd2], capture_output=True)




def main():
    # 检查 LM Studio
    try:
        requests.get("http://127.0.0.1:1234/v1/models", timeout=5)
        print("LM Studio Connection succeeded")
    except Exception:
        print("LM Studio is not running. Please start the Server first.")
        return


    system_prompt = load_skill()
    print("Skill loaded successfully")


    hwnd = win32gui.FindWindow(None, "微信")
    if not hwnd:
        print("WeChat window not found, please open WeChat first")
        return
    print("WeChat connected successfully")


    print()
    print("=" * 40)
    print("Auto-reply enabled")
    print("model:", MODEL)
    print("Ctrl+C to stop")
    print("=" * 40)
    print()


    sent_replies = []
    history = []
    last_processed = ""


    while True:
        try:
            texts = read_messages()
            if texts:
                newest = texts[-1]


                # Skip processed messages
                if newest == last_processed:
                    time.sleep(3)
                    continue
                # Skip replies sent by yourself
                if newest in sent_replies:
                    time.sleep(3)
                    continue


                print("[Received]", newest[:50])
                reply = get_reply(system_prompt, newest, history)


                if reply and len(reply) > 0:
                    sent_replies.append(reply)
                    if len(sent_replies) > 10:
                        sent_replies.pop(0)


                    history.append({"role": "user", "content": newest})
                    history.append({"role": "assistant", "content": reply})


                    print("[Reply]", reply)
                    send_message(reply)
                    last_processed = newest
                    time.sleep(5)
                else:
                    print("[Skip] Generation failed")
                    last_processed = newest


            time.sleep(3)


        except KeyboardInterrupt:
            print("\nStopped")
            break
        except Exception as e:
            print("error:", e)
            time.sleep(5)




if __name__ == "__main__":
    main()


