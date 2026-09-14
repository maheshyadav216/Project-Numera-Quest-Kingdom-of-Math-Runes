import os
import socket
import time
import json
import threading

from arduino.app_utils import App, Bridge
from arduino.app_bricks.video_imageclassification import VideoImageClassification
from arduino.app_bricks.sound_generator import SoundGenerator

player = SoundGenerator()
player.start()

# ============================================================
# BACKGROUND MUSIC
# Uses the SAME SoundGenerator as voice/SFX so the audio device
# is not opened by a separate aplay/pw-play process.
# ============================================================

MUSIC_FILES = {
    "stage1": "assets/Blue-Deer-Studio.wav",
    "stage2": "assets/Alpha-Mission.wav",
    "stage3": "assets/Horizons.wav",
}

music_event = threading.Event()
music_lock = threading.Lock()
current_music = None


def music_loop():
    global current_music

    while True:
        music_event.wait()

        if not music_event.is_set():
            continue

        music_name = current_music
        music_path = MUSIC_FILES.get(music_name)

        if music_path is None:
            music_event.clear()
            continue

        print(f"MUSIC: STARTED {music_path}")

        try:
            # Play the complete track, then restart it while music is enabled.
            player.play_wav(music_path, block=True)
        except Exception as e:
            print(f"MUSIC ERROR: {e}")
            time.sleep(0.2)

        # If music was stopped during playback, do not restart it.
        if not music_event.is_set():
            print("MUSIC: STOPPED")
        elif current_music != music_name:
            # A different stage was requested; the next iteration uses it.
            pass


def music_start(stage):
    global current_music

    music_path = MUSIC_FILES.get(stage)
    if music_path is None:
        print(f"MUSIC: Unknown stage {stage}")
        return

    with music_lock:
        current_music = stage
        music_event.set()

    print(f"MUSIC: REQUEST START {music_path}")


def music_stop():
    with music_lock:
        music_event.clear()

    try:
        player.stop()
    except Exception as e:
        print(f"MUSIC STOP ERROR: {e}")

    print("MUSIC: STOPPED")


music_thread = threading.Thread(
    target=music_loop,
    daemon=True
)
music_thread.start()


print("DISPLAY =", os.environ.get("DISPLAY"))
print("XDG_SESSION_TYPE =", os.environ.get("XDG_SESSION_TYPE"))
print("WAYLAND_DISPLAY =", os.environ.get("WAYLAND_DISPLAY"))


# ============================================================
# VIDEO IMAGE CLASSIFICATION
# ============================================================

CONFIDENCE_THRESHOLD = 0.50

detection_stream = VideoImageClassification(
    confidence=CONFIDENCE_THRESHOLD,
    debounce_sec=0.5
)


def on_detection(classifications):
    if classifications:
        label, confidence = max(
            classifications.items(),
            key=lambda item: item[1]
        )

        print(f"CLASSIFICATION CALLBACK: {label} = {confidence:.3f}")

        send_detection(label, confidence)

    else:
        print("CLASSIFICATION CALLBACK: unknown")

        send_detection("unknown", 0.0)


detection_stream.on_detect_all(on_detection)


# ============================================================
# NETWORK HANDSHAKE
# ============================================================

HOST_IP = "172.17.0.1"
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("0.0.0.0", 0))
sock.settimeout(1.0)

print(f"App Lab hunting for Host OS at {HOST_IP}...")

host_addr = None
connected = False

while not connected:
    try:
        sock.sendto(b"PING", (HOST_IP, UDP_PORT))
        data, addr = sock.recvfrom(1024)

        if data == b"ACK":
            host_addr = addr
            print(f"Target Acquired! Connected to OS at {host_addr}")
            connected = True

    except socket.timeout:
        pass


sock.settimeout(None)


# ============================================================
# SHARED STATE & WATCHDOG
# ============================================================

latest_state = {
    "x": 0.0,
    "y": 0.0,
    "a": 0,
    "b": 0
}

last_packet_time = time.monotonic()


# ============================================================
# BACKGROUND UDP RECEIVER
# ============================================================

def udp_receiver():
    global latest_state, last_packet_time

    while True:
        try:
            data, _ = sock.recvfrom(1024)
            message = json.loads(data.decode())

            # ------------------------------------------------
            # GAME CONTROLLER DATA
            # ------------------------------------------------

            if message.get("type") != "sound":
                latest_state = message
                last_packet_time = time.monotonic()

            # ------------------------------------------------
            # GAME AUDIO COMMAND
            # ------------------------------------------------

            elif message.get("type") == "sound":

                sound_name = message.get("sound")

                if sound_name == "stage1_music":
                    music_start("stage1")

                elif sound_name == "stage2_music":
                    music_start("stage2")

                elif sound_name == "stage3_music":
                    music_start("stage3")

                elif sound_name == "music_stop":
                    music_stop()

                elif sound_name == "welcome":
                    print("AUDIO: Playing welcome.wav")
                    player.play_wav(
                        "assets/welcome.wav",
                        block=True
                    )

                elif sound_name == "quest_start":
                    print("AUDIO: Playing quest_start.wav")
                    player.play_wav(
                        "assets/quest_start.wav",
                        block=True
                    )

                    print("AUDIO: Playing show_hand.wav")
                    player.play_wav(
                        "assets/show_hand.wav",
                        block=False
                    )

                elif sound_name == "answer_1":
                    print("AUDIO: Playing answer_1.wav")
                    player.play_wav("assets/answer_1.wav", block=False)

                elif sound_name == "answer_2":
                    print("AUDIO: Playing answer_2.wav")
                    player.play_wav("assets/answer_2.wav", block=False)

                elif sound_name == "answer_3":
                    print("AUDIO: Playing answer_3.wav")
                    player.play_wav("assets/answer_3.wav", block=False)

                elif sound_name == "answer_4":
                    print("AUDIO: Playing answer_4.wav")
                    player.play_wav("assets/answer_4.wav", block=False)

                elif sound_name == "answer_5":
                    print("AUDIO: Playing answer_5.wav")
                    player.play_wav("assets/answer_5.wav", block=False)

                elif sound_name == "show_hand_again":
                    print("AUDIO: Playing show_hand_again.wav")
                    player.play_wav("assets/show_hand_again.wav", block=False)

                elif sound_name == "wrong_buzzer":
                    print("AUDIO: Playing wrong-buzzer-sound.wav")
                    player.play_wav(
                        "assets/wrong-buzzer-sound.wav",
                        block=False
                    )

                elif sound_name == "collision_error":
                    print("AUDIO: Playing error-Sound.wav")
                    player.play_wav(
                        "assets/error-Sound.wav",
                        block=False
                    )

                elif sound_name == "wrong_answer_try_again":
                    print("AUDIO: Playing Wrong-answer-Try-Again.wav")
                    player.play_wav(
                        "assets/Wrong-answer-Try-Again.wav",
                        block=False
                    )

                elif sound_name == "two_tries_left":
                    print("AUDIO: Playing two_tries_left.wav")
                    player.play_wav(
                        "assets/two_tries_left.wav",
                        block=False
                    )

                elif sound_name == "last_try":
                    print("AUDIO: Playing Last_try.wav")
                    player.play_wav(
                        "assets/Last_try.wav",
                        block=False
                    )

                elif sound_name == "challenge_failed":
                    print("AUDIO: Playing Challenge_failed_Try_Again.wav")
                    player.play_wav(
                        "assets/Challenge_failed_Try_Again.wav",
                        block=False
                    )

                elif sound_name == "correct_answer":
                    print("AUDIO: Playing Correct_Answer.wav")
                    player.play_wav(
                        "assets/Correct_Answer.wav",
                        block=True
                    )

                elif sound_name == "success":
                    print("AUDIO: Playing Success-Sound.wav")
                    player.play_wav(
                        "assets/Success-Sound.wav",
                        block=True
                    )

                elif sound_name == "victory":
                    print("AUDIO: Playing victory-sound.wav")
                    player.play_wav(
                        "assets/victory-sound.wav",
                        block=False
                    )

        except Exception:
            pass


def send_detection(label, confidence):
    if host_addr is not None:
        message = {
            "type": "finger",
            "label": label,
            "confidence": confidence
        }
        sock.sendto(json.dumps(message).encode(), host_addr)


listener = threading.Thread(target=udp_receiver, daemon=True)
listener.start()


# ============================================================
# GAME / CONTROLLER LOOP
# ============================================================

def game_loop():

    global last_packet_time

    print("Entering Game Loop...")

    last_sent_command = None

    while True:

        current_time = time.monotonic()

        # ----------------------------------------------------
        # WATCHDOG
        # ----------------------------------------------------

        if current_time - last_packet_time > 0.5:

            safe_state = {
                "x": 0.0,
                "y": 0.0,
                "a": 0,
                "b": 0
            }

            print(
                "WATCHDOG: Controller lost! "
                "Neutralizing inputs and searching for host..."
            )

            sock.sendto(
                b"PING",
                (HOST_IP, UDP_PORT)
            )

        else:

            safe_state = latest_state


        # ----------------------------------------------------
        # GAME LOGIC / BRIDGE COMMANDS
        # ----------------------------------------------------

        current_action = None


        if safe_state["x"] > 0.5:

            current_action = "move_right"

        elif safe_state["x"] < -0.5:

            current_action = "move_left"

        elif safe_state["y"] < -0.5:

            current_action = "move_up"

        elif safe_state["y"] > 0.5:

            current_action = "move_down"

        elif safe_state["a"] == 1:

            current_action = "button_a"

        elif safe_state.get("b", 0) == 1:

            current_action = "button_b"


        # ----------------------------------------------------
        # EDGE TRIGGERING
        # ----------------------------------------------------

        if (
            current_action
            and current_action != last_sent_command
        ):

            Bridge.notify(current_action)

            print(
                f"Sent to Matrix: {current_action}"
            )

            last_sent_command = current_action


        if not current_action:

            last_sent_command = None


        time.sleep(1 / 30)


# Start existing game/controller processing in background
game_thread = threading.Thread(
    target=game_loop,
    daemon=True
)

game_thread.start()


# ============================================================
# START APP / BRICKS
# ============================================================

print("Numera Quest App starting...")
print("Video Image Classification is active.")
print("Show fingers to the camera.")
print("============================================================")

App.run()
