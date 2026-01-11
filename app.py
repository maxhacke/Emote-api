import os, asyncio, threading, random
from flask import Flask, request, jsonify
from datetime import datetime
from cfonts import render

# Original modules
from xC4 import *
from xHeaders import *
from Pb2 import DEcwHisPErMsG_pb2, MajoRLoGinrEs_pb2, PorTs_pb2, MajoRLoGinrEq_pb2, sQ_pb2, Team_msg_pb2

# ---------------------- FLASK APP ----------------------
app = Flask(__name__)

def get_random_color():
    colors = [
        "[FF0000]", "[00FF00]", "[0000FF]", "[FFFF00]", "[FF00FF]", "[00FFFF]", "[FFFFFF]", "[FFA500]"
    ]
    return random.choice(colors)

@app.route('/join')
def join_team():
    team_code = request.args.get('tc')
    emote_id_str = request.args.get('emote_id')

    # UID parameters (supporting 6)
    uid1 = request.args.get('uid1')
    uid2 = request.args.get('uid2')
    uid3 = request.args.get('uid3')
    uid4 = request.args.get('uid4')
    uid5 = request.args.get('uid5')
    uid6 = request.args.get('uid6')

    if not team_code or not emote_id_str:
        return jsonify({"status": "error", "message": "Missing tc or emote_id"})

    try:
        emote_id = int(emote_id_str)
    except:
        return jsonify({"status": "error", "message": "emote_id must be integer"})

    uids = [uid for uid in [uid1, uid2, uid3, uid4, uid5, uid6] if uid]

    if not uids:
        return jsonify({"status": "error", "message": "Provide at least one UID"})

    asyncio.run_coroutine_threadsafe(
        perform_emote(team_code, uids, emote_id), loop
    )

    return jsonify({
        "status": "success",
        "team_code": team_code,
        "uids": uids,
        "emote_id": emote_id,
        "message": "Emote triggered"
    })

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------- BOT FUNCTIONS ----------------------
async def perform_emote(team_code: str, uids: list, emote_id: int):
    global key, iv, region, online_writer, BOT_UID
    if online_writer is None:
        raise Exception("Bot not connected")
    try:
        # Join squad
        EM = await GenJoinSquadsPacket(team_code, key, iv)
        await SEndPacKeT(None, online_writer, 'OnLine', EM)
        await asyncio.sleep(0.12)

        # Perform emote for all UIDs
        for uid_str in uids:
            uid = int(uid_str)
            H = await Emote_k(uid, emote_id, key, iv, region)
            await SEndPacKeT(None, online_writer, 'OnLine', H)

        # Leave squad
        LV = await ExiT(BOT_UID, key, iv)
        await SEndPacKeT(None, online_writer, 'OnLine', LV)
        await asyncio.sleep(0.03)
        return {"status": "success", "message": "Emote done & bot left instantly"}
    except Exception as e:
        raise Exception(f"Failed to perform emote: {str(e)}")

# ---------------------- MAIN BOT ----------------------
async def main_bot():
    global loop, key, iv, region, BOT_UID, online_writer

    BOT_UID = int('14383895022')  # Fixed bot UID
    Uid, Pw = '4395438089', '01D3E7267895FDC4D109BB86CF15FF7388DD68A537974D3AA7533AE2E24A2501'

    open_id, access_token = await GeNeRaTeAccEss(Uid, Pw)
    if not open_id or not access_token:
        print("Error - Invalid account")
        return None

    PyL = await EncRypTMajoRLoGin(open_id, access_token)
    MajoRLoGinResPonsE = await MajorLogin(PyL)
    if not MajoRLoGinResPonsE:
        print("Error - Account banned or not registered!")
        return None

    MajoRLoGinauTh = await DecRypTMajoRLoGin(MajoRLoGinResPonsE)
    UrL = MajoRLoGinauTh.url
    print(UrL)
    region = MajoRLoGinauTh.region
    ToKen = MajoRLoGinauTh.token
    TarGeT = MajoRLoGinauTh.account_uid
    key = MajoRLoGinauTh.key
    iv = MajoRLoGinauTh.iv
    timestamp = MajoRLoGinauTh.timestamp

    loop = asyncio.get_running_loop()

    LoGinDaTa = await GetLoginData(UrL, PyL, ToKen)
    if not LoGinDaTa:
        print("Error getting login data!")
        return None

    LoGinDaTaUncRypTinG = await DecRypTLoGinDaTa(LoGinDaTa)
    OnLinePorTs = LoGinDaTaUncRypTinG.Online_IP_Port
    ChaTPorTs = LoGinDaTaUncRypTinG.AccountIP_Port
    OnLineiP, OnLineporT = OnLinePorTs.split(":")
    ChaTiP, ChaTporT = ChaTPorTs.split(":")

    AutHToKen = await xAuThSTarTuP(int(TarGeT), ToKen, int(timestamp), key, iv)
    ready_event = asyncio.Event()

    task1 = asyncio.create_task(
        TcPChaT(ChaTiP, ChaTporT, AutHToKen, key, iv, LoGinDaTaUncRypTinG, ready_event, region)
    )
    await ready_event.wait()
    await asyncio.sleep(1)

    task2 = asyncio.create_task(
        TcPOnLine(OnLineiP, OnLineporT, key, iv, AutHToKen)
    )

    os.system('clear')
    print(render('DEV', colors=['white', 'green'], align='center'))
    print(f"\n - Bot starting and online on target: {TarGeT}")
    print(" - Bot status > Good | Online (: \n")

    await asyncio.gather(task1, task2)

# Restarting bot on timeout
async def bot_runner():
    while True:
        try:
            await asyncio.wait_for(main_bot(), timeout=7*60*60)
        except asyncio.TimeoutError:
            print("Token expired, restarting...")
        except Exception as e:
            print(f"Error TCP - {e}, restarting...")

# ---------------------- ENTRY POINT ----------------------
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    asyncio.run(bot_runner())
