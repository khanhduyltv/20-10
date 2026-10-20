import os
import json
import urllib.request
import sqlite3
import secrets
import socket
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort


app = Flask(__name__)
DB_PATH = "gifts2010.db"

# ==========================================
# KHO LỜI CHÚC 20/10 PHONG PHÚ THEO CHỦ ĐỀ
# ==========================================
WISHES_DB = {
    "me": [
        "Nhân ngày Phụ nữ Việt Nam 20/10, con chúc Mẹ yêu luôn mạnh khỏe, bình an và mãi nở nụ cười hiền hậu. Cảm ơn Mẹ vì cả cuộc đời tần tảo hy sinh cho chúng con!",
        "20/10 chúc người phụ nữ vĩ đại nhất đời con luôn trẻ khỏe, hạnh phúc và chẳng còn những nỗi lo toan. Với con, Mẹ mãi là bầu trời bình yên nhất!",
        "Chúc Mẹ yêu ngày 20/10 ngập tràn niềm vui và hoa tươi. Mong mỗi ngày trôi qua của Mẹ đều nhẹ nhàng, an nhiên và tràn đầy tiếng cười bên gia đình mình.",
        "Không có bông hoa nào đẹp bằng nụ cười của Mẹ. Nhân ngày 20/10, con chúc Mẹ thật nhiều sức khỏe để con được chăm sóc và báo hiếu Mẹ thật lâu!",
        "Gửi ngàn lời yêu thương nhất đến Mẹ nhân ngày 20/10! Chúc Mẹ của con luôn vui vẻ, trẻ trung và mãi là điểm tựa ấm áp nhất của cả nhà."
    ],
    "nguoi_yeu": [
        "Chúc công chúa của anh ngày 20/10 thật ngọt ngào, rạng rỡ như đóa hoa hồng buổi sớm. Cảm ơn em đã đến và làm thế giới của anh trở nên dịu dàng hơn bao giờ hết!",
        "20/10 chúc người thương của anh luôn xinh đẹp, hạnh phúc và bình yên trong vòng tay anh. Thế giới ngoài kia có bão giông thế nào thì về bên anh nhé!",
        "Gửi đến cô gái đang đọc những dòng này: Chúc em ngày 20/10 ngập tràn niềm vui, luôn giữ nụ cười tỏa nắng từng làm anh rung động ngay từ lần đầu gặp gỡ.",
        "Hôm nay là 20/10, chúc vợ/người yêu của anh ngày càng xinh đẹp, mọi điều ước đều thành hiện thực và mãi yêu thương anh như bây giờ nhé!",
        "Người ta tặng hoa cho cả thế giới vào ngày 20/10, còn anh chỉ muốn gói trọn cả thế giới dịu dàng nhất dành tặng riêng cho một mình em!"
    ],
    "crush": [
        "Nhân ngày 20/10, chúc cậu luôn xinh đẹp, yêu đời và gặp thật nhiều may mắn. Bật mí nhỏ là nụ cười của cậu làm tim ai đó lỡ nhịp suốt đấy!",
        "20/10 chúc cô gái đáng yêu nhất hệ Mặt Trời luôn rạng rỡ như hoa hướng dương. Mong rằng những điều dịu dàng nhất sẽ luôn tìm đến bên cậu!",
        "Chúc cậu một ngày 20/10 thật đặc biệt, ngập tràn hoa và quà. Nếu hôm nay chưa có ai làm cậu cười, hy vọng món quà nhỏ này sẽ làm được điều đó!",
        "Gửi chút nắng ấm và ngàn đóa hoa nhân ngày 20/10 đến người tớ thầm thương. Chúc cậu luôn bình yên, xinh đẹp và sớm nhận ra tín hiệu từ tớ nhé!"
    ],
    "ban_be": [
        "Chúc các chị em đồng nghiệp và bạn bè ngày 20/10 nhan sắc thăng hạng, tiền tài rực rỡ, công việc hanh thông và luôn tràn đầy năng lượng tích cực!",
        "Nhân ngày 20/10, chúc bạn tôi luôn xinh đẹp tuyệt vời, lương thưởng ngập tài khoản, deadline tự động qua môn và sớm tìm được bến đỗ hạnh phúc!",
        "Chúc một nửa thế giới ngày 20/10 thật tưng bừng! Mong bạn luôn tự tin, độc lập, kiêu hãnh và tỏa sáng theo cách riêng rực rỡ nhất của mình.",
        "20/10 chúc cô bạn thân của tôi ăn mãi không béo, tiền tiêu không hết, ngày càng trẻ đẹp và lúc nào cũng tươi cười rạng rỡ nhé!"
    ],
    "co_sep": [
        "Nhân ngày Phụ nữ Việt Nam 20/10, kính chúc Cô/Sếp luôn dồi dào sức khỏe, hạnh phúc viên mãn và gặt hái thêm nhiều thành công rực rỡ trong sự nghiệp!",
        "Gửi lời tri ân sâu sắc nhất nhân ngày 20/10. Chúc Cô/Chị luôn giữ vững ngọn lửa nhiệt huyết, trẻ trung, xinh đẹp và mãi là người truyền cảm hứng tuyệt vời!",
        "Chúc mừng ngày 20/10! Kính chúc Chị/Cô luôn rạng ngời sắc xuân, công việc thuận buồm xuôi gió và tràn ngập niềm vui bên gia đình thân yêu."
    ],
    "hai_huoc": [
        "Chúc bạn 20/10: Nhan sắc 'kịch trần', tiền tiêu 'phất phới', tình duyên 'tới tấp' và cân nặng luôn ở mức 'đỉnh của chóp'!",
        "Thông báo khẩn ngày 20/10: Chúc chị em hôm nay không phải rửa bát, không lo tăng cân, ví tiền dày cộp và nhận quà mỏi cả hai tay!",
        "20/10 chúc bạn trẻ mãi không già, sắc đẹp vượt thời gian, ví tiền vượt không gian và độ lầy lội thì không ai sánh bằng!",
        "Thay mặt Hội Đẹp Trai Toàn Cầu, chúc bạn ngày 20/10 xinh đẹp bất chấp cam thường, giàu sang bất chấp thị trường nhé!"
    ]
}

# ==========================================
# KHỞI TẠO CƠ SỞ DỮ LIỆU SQLITE
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS gifts (
            id TEXT PRIMARY KEY,
            sender TEXT,
            receiver TEXT,
            category TEXT,
            message TEXT,
            flower_type TEXT,
            theme_color TEXT,
            views INTEGER DEFAULT 0,
            hearts INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

FALLBACK_NGROK_URL = "https://donn-frightenable-unperipherally.ngrok-free.dev"

def get_ngrok_url():
    """Tự động phát hiện public URL của ngrok đang chạy qua Ngrok Client API (127.0.0.1:4040)"""
    try:
        req = urllib.request.Request("http://127.0.0.1:4040/api/tunnels", headers={"User-Agent": "Flask"})
        with urllib.request.urlopen(req, timeout=1.2) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            tunnels = data.get("tunnels", [])
            for t in tunnels:
                if t.get("proto") == "https":
                    return t.get("public_url")
            if tunnels:
                return tunnels[0].get("public_url")
    except Exception:
        pass
    return FALLBACK_NGROK_URL

def get_base_url():
    """Lấy URL gốc ưu tiên theo domain deploy/ngrok để tạo QR quét được từ mọi mạng"""
    forwarded_host = request.headers.get("X-Forwarded-Host")
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "https")
    if forwarded_host:
        return f"{forwarded_proto}://{forwarded_host}"

    if "onrender.com" in request.host:
        return f"https://{request.host}"

    if "ngrok" in request.host:
        proto = "https" if (request.is_secure or forwarded_proto == "https") else request.scheme
        return f"{proto}://{request.host}"

    # 2. Nếu đang chạy ngrok ở máy, ưu tiên link ngrok để QR sinh ra quét được trên điện thoại
    ngrok = get_ngrok_url()
    if ngrok:
        return ngrok

    # 3. Fallback IP LAN nếu không bật ngrok
    local_ip = get_local_ip()
    port = request.host.split(":")[-1] if ":" in request.host else "5000"
    return f"http://{local_ip}:{port}"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# ==========================================
# TỰ ĐỘNG TẠO 2 TRANG HTML TÁCH BIỆT
# ==========================================
CREATE_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Studio Tạo Thiệp & Mã QR 20/10</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 15% 15%, #fff0f5 0%, #ffe4ee 45%, #fce7f3 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        .font-serif-title { font-family: 'Playfair Display', serif; }
        .font-script { font-family: 'Dancing Script', cursive; }
        .glass-panel {
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(244, 63, 94, 0.18);
            box-shadow: 0 20px 50px rgba(190, 18, 60, 0.08);
        }
        .flower-option.active {
            border-color: #e11d48;
            background: #fff1f2;
            box-shadow: 0 8px 20px rgba(225, 29, 72, 0.15);
            transform: translateY(-2px);
        }
        .cat-chip.active {
            background: linear-gradient(135deg, #e11d48, #be185d);
            color: white;
            border-color: transparent;
            box-shadow: 0 6px 15px rgba(225, 29, 72, 0.25);
        }
    </style>
</head>
<body class="text-rose-950 py-8 px-4 sm:px-6">
    <div class="max-w-6xl mx-auto">
        <!-- Header -->
        <header class="text-center mb-10">
            <span class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-100 border border-rose-200 text-rose-700 text-xs font-bold tracking-wider uppercase mb-3">
                ✨ Studio Tạo Quà & QR 20/10 (Tách Trang Độc Lập)
            </span>
            <h1 class="font-serif-title text-3xl sm:text-5xl font-bold text-rose-900 mb-3">
                Tạo Hộp Quà 3D & Mã QR <span class="text-rose-600 italic">20/10</span>
            </h1>
            <p class="text-rose-800/75 max-w-2xl mx-auto text-sm sm:text-base">
                Tạo lời chúc riêng hoặc xoay ngẫu nhiên, hệ thống sẽ sinh <b>Link ngắn & Mã QR riêng biệt</b>. Khi người nhận quét mã sẽ mở thẳng ra <b>Trang Hộp Quà & Bó Hoa 3D</b> tuyệt đẹp!
            </p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <!-- CỘT TRÁI: FORM CẤU HÌNH QUÀ & LỜI CHÚC -->
            <div class="lg:col-span-7 glass-panel rounded-3xl p-6 sm:p-8">
                <div class="flex items-center justify-between mb-6 pb-4 border-b border-rose-100">
                    <div>
                        <h2 class="font-serif-title text-2xl font-bold text-rose-900">1. Thiết Kế Món Quà 20/10</h2>
                        <p class="text-xs text-rose-600/80">Tùy chỉnh thông tin & lời chúc dành cho người nhận</p>
                    </div>
                    <span class="text-3xl">🎁</span>
                </div>

                <!-- Tên người gửi & người nhận -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-5">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-rose-800 mb-1.5">Dành tặng cho *</label>
                        <input id="receiverInput" type="text" value="Người Phụ Nữ Tuyệt Vời" placeholder="VD: Mẹ yêu, Em yêu, Thu Hà..."
                            class="w-full px-4 py-3 rounded-xl border border-rose-200 bg-white/90 focus:outline-none focus:ring-2 focus:ring-rose-500 font-medium text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-rose-800 mb-1.5">Người gửi</label>
                        <input id="senderInput" type="text" value="Một người luôn yêu thương bạn" placeholder="VD: Con trai của Mẹ, Anh..."
                            class="w-full px-4 py-3 rounded-xl border border-rose-200 bg-white/90 focus:outline-none focus:ring-2 focus:ring-rose-500 font-medium text-sm">
                    </div>
                </div>

                <!-- Chọn chủ đề & Random lời chúc -->
                <div class="mb-5">
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                        <label class="text-xs font-bold uppercase tracking-wider text-rose-800">Chủ đề lời chúc</label>
                        <button type="button" onclick="fetchRandomWish()"
                            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-amber-500 to-rose-500 text-white text-xs font-bold shadow hover:opacity-95 active:scale-95 transition">
                            🎲 Đổi Lời Chúc Ngẫu Nhiên
                        </button>
                    </div>

                    <div class="flex flex-wrap gap-2 mb-3" id="categoryChips">
                        <button type="button" data-cat="all" class="cat-chip active px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">✨ Tất cả</button>
                        <button type="button" data-cat="nguoi_yeu" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">❤️ Vợ / Người yêu</button>
                        <button type="button" data-cat="me" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">🌷 Mẹ yêu</button>
                        <button type="button" data-cat="crush" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">💌 Crush</button>
                        <button type="button" data-cat="ban_be" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">🥂 Bạn bè & Đồng nghiệp</button>
                        <button type="button" data-cat="co_sep" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">💐 Cô giáo / Sếp</button>
                        <button type="button" data-cat="hai_huoc" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">😂 Hài hước</button>
                    </div>

                    <textarea id="messageInput" rows="4"
                        class="w-full px-4 py-3 rounded-2xl border border-rose-200 bg-white/95 focus:outline-none focus:ring-2 focus:ring-rose-500 text-sm leading-relaxed"
                        placeholder="Nhập lời chúc 20/10 hoặc bấm nút Đổi Lời Chúc Ngẫu Nhiên...">Nhân ngày Phụ nữ Việt Nam 20/10, chúc bạn luôn xinh đẹp rạng ngời như những đóa hoa tươi thắm, ngập tràn niềm vui và hạnh phúc trọn vẹn!</textarea>
                </div>

                <!-- Chọn loại bó hoa nở ra khi mở hộp quà -->
                <div class="mb-6">
                    <label class="block text-xs font-bold uppercase tracking-wider text-rose-800 mb-2.5">Chọn Bó Hoa 3D Trong Hộp Quà</label>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3" id="flowerSelector">
                        <div data-flower="rose" class="flower-option active cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3 text-center transition">
                            <div class="text-3xl mb-1">🌹</div>
                            <div class="text-xs font-bold text-rose-900">Hồng Nhung Đỏ</div>
                            <div class="text-[10px] text-rose-500">Nồng nàn & Lãng mạn</div>
                        </div>
                        <div data-flower="tulip" class="flower-option cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3 text-center transition">
                            <div class="text-3xl mb-1">🌷</div>
                            <div class="text-xs font-bold text-rose-900">Tulip Pastel</div>
                            <div class="text-[10px] text-rose-500">Dịu dàng & Thanh lịch</div>
                        </div>
                        <div data-flower="sunflower" class="flower-option cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3 text-center transition">
                            <div class="text-3xl mb-1">🌻</div>
                            <div class="text-xs font-bold text-rose-900">Hướng Dương</div>
                            <div class="text-[10px] text-rose-500">Rạng rỡ & Ấm áp</div>
                        </div>
                        <div data-flower="peony" class="flower-option cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3 text-center transition">
                            <div class="text-3xl mb-1">🌺</div>
                            <div class="text-xs font-bold text-rose-900">Mẫu Đơn Hoàng Gia</div>
                            <div class="text-[10px] text-rose-500">Cao quý & Viên mãn</div>
                        </div>
                    </div>
                </div>

                <!-- Cấu hình Domain/IP cho QR (Tự động nhận link Ngrok) -->
                <div class="mb-6 p-3.5 rounded-2xl bg-rose-50/90 border border-rose-200/70">
                    <div class="flex items-center justify-between mb-1">
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-rose-700">
                            🌐 Địa chỉ Server tạo QR (Ưu tiên Ngrok để quét trên 4G/mọi mạng)
                        </label>
                        <span class="text-[10px] bg-rose-600 text-white font-bold px-2 py-0.5 rounded-full shadow-sm">Ngrok Ready</span>
                    </div>
                    <input id="baseUrlInput" type="text" value="{{ default_base_url }}"
                        class="w-full px-3 py-2 rounded-lg border border-rose-200 bg-white text-xs font-mono text-rose-900">
                    <p class="text-[11px] text-rose-600/80 mt-1">💡 Link này sẽ gắn trực tiếp vào Mã QR. Điện thoại quét sẽ mở thẳng trang quà qua link này.</p>
                </div>

                <button type="button" onclick="createGiftLink()"
                    class="w-full py-4 rounded-2xl bg-gradient-to-r from-rose-600 via-pink-600 to-rose-500 text-white font-bold text-base shadow-xl shadow-rose-500/25 hover:brightness-105 active:scale-[0.99] transition flex items-center justify-center gap-2">
                    <span>✨ Tạo Trang Quà Tặng Riêng & Sinh Mã QR</span>
                </button>
            </div>

            <!-- CỘT PHẢI: THẺ QR & TRẠNG THÁI MỞ QUÀ -->
            <div class="lg:col-span-5 glass-panel rounded-3xl p-6 sm:p-8 text-center sticky top-6">
                <h2 class="font-serif-title text-2xl font-bold text-rose-900 mb-1">2. Thẻ Quét QR Tặng Quà</h2>
                <p class="text-xs text-rose-600/80 mb-5">Quét bằng Camera hoặc Zalo sẽ mở thẳng sang <b>Trang Mở Quà 3D</b></p>

                <!-- Khung Poster QR -->
                <div id="qrPosterCard" class="mx-auto max-w-xs rounded-3xl p-6 bg-gradient-to-b from-fff5f7 to-ffe4e6 border-2 border-rose-200 shadow-inner relative overflow-hidden"
                     style="background: linear-gradient(160deg, #fff5f7 0%, #ffe4ec 100%);">
                    <div class="text-xs font-bold tracking-widest uppercase text-rose-500 mb-1">HAPPY WOMEN'S DAY 20/10</div>
                    <div id="posterReceiver" class="font-script text-3xl text-rose-800 mb-4 truncate">Người Phụ Nữ Tuyệt Vời</div>

                    <div class="bg-white p-4 rounded-2xl shadow-md inline-block border border-rose-100 mx-auto mb-3">
                        <div id="qrcodeContainer" class="flex items-center justify-center min-h-[190px] min-w-[190px]"></div>
                    </div>

                    <p class="text-xs font-semibold text-rose-700">📱 Quét mã để mở Hộp Quà & Bó Hoa 3D</p>
                    <p id="posterSender" class="text-[11px] text-rose-500 mt-1 italic">Từ: Một người luôn yêu thương bạn</p>
                </div>

                <!-- Link trang quà tách biệt -->
                <div id="giftLinkBox" class="mt-5 hidden">
                    <div class="text-xs font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-xl px-3 py-2 mb-3">
                        ✅ Đã tạo Trang Quà Tặng độc lập thành công!
                    </div>

                    <div class="flex items-center gap-2 mb-3">
                        <input id="shortUrlOutput" readonly type="text"
                            class="w-full px-3 py-2.5 rounded-xl bg-white border border-rose-200 text-xs font-mono text-rose-900">
                        <button onclick="copyGiftUrl()" class="px-3.5 py-2.5 rounded-xl bg-rose-100 hover:bg-rose-200 text-rose-800 text-xs font-bold shrink-0 transition">
                            Copy
                        </button>
                    </div>

                    <div class="grid grid-cols-2 gap-2.5 mb-3">
                        <a id="openGiftPageBtn" href="#" target="_blank"
                            class="py-3 px-4 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow transition flex items-center justify-center gap-1.5">
                            🎁 Mở Trang Nhận Quà
                        </a>
                        <button onclick="downloadPosterPNG()"
                            class="py-3 px-4 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow transition flex items-center justify-center gap-1.5">
                            📥 Tải Ảnh QR (PNG)
                        </button>
                    </div>

                    <!-- Thống kê thời gian thực -->
                    <div class="p-3 rounded-xl bg-white/80 border border-rose-100 flex items-center justify-around text-xs">
                        <div>
                            <span class="text-rose-500">👁️ Lượt mở quà:</span>
                            <b id="statViews" class="text-rose-900 ml-1">0</b>
                        </div>
                        <div class="h-4 w-px bg-rose-200"></div>
                        <div>
                            <span class="text-rose-500">❤️ Tim cảm ơn:</span>
                            <b id="statHearts" class="text-rose-600 ml-1">0</b>
                        </div>
                        <button onclick="refreshStats()" class="text-[11px] text-rose-600 underline font-semibold">Làm mới</button>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let selectedCategory = 'all';
        let selectedFlower = 'rose';
        let currentGiftId = null;
        let currentGiftUrl = '';

        // Chọn chủ đề lời chúc
        document.querySelectorAll('.cat-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.cat-chip').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedCategory = btn.dataset.cat;
                fetchRandomWish();
            });
        });

        // Chọn loại hoa
        document.querySelectorAll('.flower-option').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.flower-option').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                selectedFlower = card.dataset.flower;
            });
        });

        // Lấy lời chúc ngẫu nhiên từ Server Python
        async function fetchRandomWish() {
            const res = await fetch(`/api/random-wish?category=${selectedCategory}`);
            const data = await res.json();
            const msgEl = document.getElementById('messageInput');
            msgEl.value = data.wish;
        }

        // Gửi dữ liệu lên Server Python để tạo trang quà độc lập
        async function createGiftLink() {
            const receiver = document.getElementById('receiverInput').value.trim() || 'Người Phụ Nữ Tuyệt Vời';
            const sender = document.getElementById('senderInput').value.trim() || 'Một người luôn yêu thương bạn';
            const message = document.getElementById('messageInput').value.trim();
            const baseUrl = document.getElementById('baseUrlInput').value.trim().replace(/\/$/, '');

            const res = await fetch('/api/create-gift', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    receiver,
                    sender,
                    category: selectedCategory,
                    message,
                    flower_type: selectedFlower
                })
            });
            const data = await res.json();
            currentGiftId = data.id;
            currentGiftUrl = `${baseUrl}/qua/${data.id}`;

            document.getElementById('posterReceiver').textContent = receiver;
            document.getElementById('posterSender').textContent = `Từ: ${sender}`;

            // Vẽ QR Code cực thoáng vì URL ngắn
            const qrContainer = document.getElementById('qrcodeContainer');
            qrContainer.innerHTML = '';
            new QRCode(qrContainer, {
                text: currentGiftUrl,
                width: 190,
                height: 190,
                colorDark: "#881337",
                colorLight: "#ffffff",
                correctLevel: QRCode.CorrectLevel.M
            });

            document.getElementById('shortUrlOutput').value = currentGiftUrl;
            document.getElementById('openGiftPageBtn').href = currentGiftUrl;
            document.getElementById('giftLinkBox').classList.remove('hidden');
            refreshStats();
        }

        async function refreshStats() {
            if (!currentGiftId) return;
            const res = await fetch(`/api/stats/${currentGiftId}`);
            if (res.ok) {
                const data = await res.json();
                document.getElementById('statViews').textContent = data.views;
                document.getElementById('statHearts').textContent = data.hearts;
            }
        }

        function copyGiftUrl() {
            const input = document.getElementById('shortUrlOutput');
            input.select();
            navigator.clipboard.writeText(input.value);
            alert('Đã sao chép link trang quà tặng!');
        }

        // Tải Poster QR PNG sắc nét
        function downloadPosterPNG() {
            const qrImg = document.querySelector('#qrcodeContainer img') || document.querySelector('#qrcodeContainer canvas');
            if (!qrImg) return;

            const canvas = document.createElement('canvas');
            canvas.width = 800;
            canvas.height = 1050;
            const ctx = canvas.getContext('2d');

            // Nền Gradient
            const grad = ctx.createLinearGradient(0, 0, 800, 1050);
            grad.addColorStop(0, '#fff0f5');
            grad.addColorStop(1, '#fecdd3');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, 800, 1050);

            // Viền vàng hồng
            ctx.strokeStyle = '#f43f5e';
            ctx.lineWidth = 6;
            ctx.strokeRect(35, 35, 730, 980);

            ctx.fillStyle = '#be123c';
            ctx.font = 'bold 26px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('HAPPY VIETNAMESE WOMEN\'S DAY 20/10', 400, 120);

            ctx.fillStyle = '#881337';
            ctx.font = 'italic bold 48px serif';
            ctx.fillText(document.getElementById('posterReceiver').textContent, 400, 195);

            // Khung trắng chứa QR
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.roundRect(190, 240, 420, 420, 30);
            ctx.fill();

            ctx.drawImage(qrImg, 225, 275, 350, 350);

            ctx.fillStyle = '#9f1239';
            ctx.font = 'bold 28px sans-serif';
            ctx.fillText('📱 Quét mã QR để mở Hộp Quà & Hoa 3D', 400, 740);

            ctx.fillStyle = '#be123c';
            ctx.font = 'italic 24px sans-serif';
            ctx.fillText(document.getElementById('posterSender').textContent, 400, 800);

            ctx.fillStyle = '#e11d48';
            ctx.font = '20px monospace';
            ctx.fillText(currentGiftUrl, 400, 940);

            const link = document.createElement('a');
            link.download = `Quatang-20-10-${currentGiftId || 'QR'}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        }

        // Tự động tạo sẵn 1 mã QR mẫu khi vừa vào trang
        window.addEventListener('DOMContentLoaded', () => {
            const baseInput = document.getElementById('baseUrlInput');
            if (baseInput && (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')) {
                baseInput.value = window.location.origin;
            }
            createGiftLink();
        });
    </script>
</body>
</html>
"""

GIFT_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Món Quà 20/10 Dành Tặng {{ gift.receiver }}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { user-select: none; -webkit-tap-highlight-color: transparent; }
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 50% 25%, #3b0a26 0%, #1a0512 65%, #0d0209 100%);
            min-height: 100vh;
            overflow-x: hidden;
            color: #fff;
        }
        .font-script { font-family: 'Dancing Script', cursive; }
        .font-serif-title { font-family: 'Playfair Display', serif; }

        /* HIỆU ỨNG HỘP QUÀ 3D SANG TRỌNG */
        .gift-stage {
            perspective: 1200px;
        }
        .gift-box-wrapper {
            cursor: pointer;
            transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: floatBox 3.2s ease-in-out infinite;
        }
        .gift-box-wrapper:hover {
            transform: scale(1.06);
        }
        @keyframes floatBox {
            0%, 100% { transform: translateY(0px) rotate(-1deg); }
            50% { transform: translateY(-16px) rotate(1.5deg); }
        }
        .shake-box {
            animation: vigorousShake 0.75s cubic-bezier(.36,.07,.19,.97) both !important;
        }
        @keyframes vigorousShake {
            0%, 100% { transform: rotate(0deg) scale(1); }
            15% { transform: rotate(-11deg) scale(1.08); }
            30% { transform: rotate(11deg) scale(1.1); }
            45% { transform: rotate(-13deg) scale(1.12); }
            60% { transform: rotate(13deg) scale(1.15); }
            75% { transform: rotate(-8deg) scale(1.18); }
        }
        .lid-open {
            transform: translateY(-150px) rotate(22deg) scale(0.85);
            opacity: 0;
            transition: all 0.85s cubic-bezier(0.22, 1, 0.36, 1);
        }

        /* HIỆU ỨNG BÓ HOA NỞ & ĐUNG ĐƯA TRONG GIÓ */
        .bouquet-appear {
            animation: bloomUp 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards, gentleSway 4.5s ease-in-out 1.1s infinite;
        }
        @keyframes bloomUp {
            0% { opacity: 0; transform: translateY(90px) scale(0.35); }
            70% { opacity: 1; transform: translateY(-8px) scale(1.04); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes gentleSway {
            0%, 100% { transform: rotate(-1.5deg) translateY(0px); }
            50% { transform: rotate(1.5deg) translateY(-6px); }
        }

        /* THƯ TAY SÁP ONG SANG TRỌNG */
        .parchment-card {
            background: linear-gradient(165deg, #fffdf9 0%, #fff1f5 55%, #ffe4ec 100%);
            box-shadow: 0 25px 70px rgba(244, 63, 94, 0.35), 0 0 0 1px rgba(251, 113, 133, 0.4);
            color: #4c0519;
        }
        .glow-aura {
            background: radial-gradient(circle, rgba(244,63,94,0.45) 0%, rgba(251,191,36,0.18) 45%, transparent 72%);
            filter: blur(25px);
        }
    </style>
</head>
<body class="relative flex flex-col items-center justify-center min-h-screen px-4 py-10">

    <!-- Canvas Cánh Hoa & Pháo Hoa Trái Tim -->
    <canvas id="petalCanvas" class="fixed inset-0 pointer-events-none z-10"></canvas>

    <!-- Nút Bật/Tắt Nhạc Góc Phải -->
    <button id="musicBtn" onclick="toggleMusic()"
        class="fixed top-5 right-5 z-50 px-4 py-2 rounded-full bg-white/15 backdrop-blur-md border border-white/25 text-xs font-semibold text-pink-100 flex items-center gap-2 hover:bg-white/25 transition shadow-lg">
        <span id="musicIcon">🎵</span> <span id="musicLabel">Nhạc 20/10</span>
    </button>

    <!-- ==================================================== -->
    <!-- MÀN HÌNH 1: HỘP QUÀ 3D BÍ ẨN CHỜ NGƯỜI NHẬN CHẠM MỞ -->
    <!-- ==================================================== -->
    <div id="stageClosed" class="relative z-20 text-center max-w-md mx-auto flex flex-col items-center">
        <div class="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-rose-500/20 border border-rose-400/30 text-rose-200 text-xs font-semibold tracking-wider uppercase mb-4">
            ✨ Happy Vietnamese Women's Day 20/10 ✨
        </div>

        <h1 class="font-serif-title text-2xl sm:text-4xl font-bold text-white mb-2">
            Món Quà Dành Riêng Cho
        </h1>
        <div class="font-script text-4xl sm:text-5xl text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-pink-300 to-rose-300 py-1 mb-8">
            {{ gift.receiver }}
        </div>

        <!-- Hộp Quà 3D SVG Tương Tác -->
        <div class="relative gift-stage my-4 flex items-center justify-center">
            <div class="glow-aura absolute w-72 h-72 rounded-full"></div>

            <div id="giftBox" onclick="openGiftSequence()" class="gift-box-wrapper relative w-64 h-64 flex flex-col items-center justify-center">
                <!-- Nắp Hộp Quà + Nơ Lụa Vàng -->
                <div id="giftLid" class="relative z-20 -mb-3 transition-transform duration-700">
                    <svg width="220" height="95" viewBox="0 0 220 95" fill="none">
                        <!-- Nơ Lụa Đôi -->
                        <path d="M110 42C85 5 45 12 55 40C62 56 95 48 110 42Z" fill="url(#goldGrad)" stroke="#fde68a" stroke-width="2"/>
                        <path d="M110 42C135 5 175 12 165 40C158 56 125 48 110 42Z" fill="url(#goldGrad)" stroke="#fde68a" stroke-width="2"/>
                        <circle cx="110" cy="42" r="11" fill="#fbbf24" stroke="#fef08a" stroke-width="3"/>
                        <!-- Thân Nắp Hộp -->
                        <rect x="15" y="46" width="190" height="42" rx="10" fill="url(#lidGrad)" stroke="#fda4af" stroke-width="2"/>
                        <rect x="96" y="46" width="28" height="42" fill="url(#goldGrad)"/>
                    </svg>
                </div>

                <!-- Thân Hộp Quà -->
                <div class="relative z-10">
                    <svg width="200" height="145" viewBox="0 0 200 145" fill="none">
                        <rect x="12" y="4" width="176" height="135" rx="14" fill="url(#boxGrad)" stroke="#fb7185" stroke-width="2"/>
                        <!-- Dải Ruy Băng Dọc & Ngang -->
                        <rect x="86" y="4" width="28" height="135" fill="url(#goldGrad)"/>
                        <rect x="12" y="58" width="176" height="24" fill="url(#goldGrad)" fill-opacity="0.9"/>
                        <!-- Trái Tim Phát Sáng Giữa Hộp -->
                        <path d="M100 84C100 84 82 72 82 61C82 54 88 50 94 50C98 50 100 53 100 53C100 53 102 50 106 50C112 50 118 54 118 61C118 72 100 84 100 84Z" fill="#fff1f2"/>
                        <defs>
                            <linearGradient id="boxGrad" x1="12" y1="4" x2="188" y2="139" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#e11d48"/>
                                <stop offset="1" stop-color="#881337"/>
                            </linearGradient>
                            <linearGradient id="lidGrad" x1="15" y1="46" x2="205" y2="88" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#f43f5e"/>
                                <stop offset="1" stop-color="#be123c"/>
                            </linearGradient>
                            <linearGradient id="goldGrad" x1="0" y1="0" x2="200" y2="140" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#fde68a"/>
                                <stop offset="0.5" stop-color="#f59e0b"/>
                                <stop offset="1" stop-color="#fcd34d"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
            </div>
        </div>

        <p class="mt-4 text-sm sm:text-base text-pink-200 font-medium animate-pulse">
            👆 Chạm vào hộp quà để mở điều bất ngờ
        </p>
        <p class="mt-1 text-xs text-pink-300/60">
            Được gửi từ: <span class="text-pink-200 font-semibold">{{ gift.sender }}</span>
        </p>
    </div>

    <!-- ============================================================ -->
    <!-- MÀN HÌNH 2: BÓ HOA 3D NỞ RỘ & BỨC THƯ TAY MỞ RA SAU KHI CHẠM -->
    <!-- ============================================================ -->
    <div id="stageOpened" class="hidden relative z-20 w-full max-w-4xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

            <!-- CỘT TRÁI: BÓ HOA NGHỆ THUẬT LỚN ĐUNG ĐƯA -->
            <div class="lg:col-span-5 flex flex-col items-center justify-center">
                <div class="relative flex items-center justify-center">
                    <div class="glow-aura absolute w-80 h-80 rounded-full"></div>
                    <div id="bouquetContainer" class="bouquet-appear relative z-10 w-72 sm:w-80"></div>
                </div>
                <div class="mt-2 px-4 py-1 rounded-full bg-white/10 border border-white/20 text-xs text-amber-200 font-medium">
                    💐 Bó hoa tươi thắm dành tặng riêng {{ gift.receiver }}
                </div>
            </div>

            <!-- CỘT PHẢI: THIỆP LỜI CHÚC PHONG BÌ SÁP ONG -->
            <div class="lg:col-span-7">
                <div class="parchment-card rounded-3xl p-6 sm:p-10 relative overflow-hidden">
                    <!-- Góc trang trí cổ điển -->
                    <div class="flex items-center justify-between border-b border-rose-200 pb-4 mb-5">
                        <div>
                            <span class="text-[11px] font-bold uppercase tracking-widest text-rose-500 block">Thiệp Chúc Mừng 20/10</span>
                            <h2 class="font-script text-3xl sm:text-4xl text-rose-800 mt-0.5">Gửi {{ gift.receiver }}</h2>
                        </div>
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-rose-600 to-pink-700 text-amber-200 flex items-center justify-center shadow-md border-2 border-amber-200 font-serif-title font-bold text-sm">
                            20/10
                        </div>
                    </div>

                    <!-- Nội dung lời chúc chạy chữ mềm mại -->
                    <div class="min-h-[130px] flex items-center">
                        <p id="typewriterText" class="text-base sm:text-lg leading-relaxed text-rose-950 font-medium whitespace-pre-line"></p>
                    </div>

                    <!-- Chữ ký người gửi -->
                    <div class="mt-6 pt-4 border-t border-rose-200/80 flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <span class="text-xs text-rose-500 block">Người gửi yêu thương,</span>
                            <span class="font-script text-2xl text-rose-800">{{ gift.sender }}</span>
                        </div>

                        <!-- Nút thả tim cảm ơn gửi về Server -->
                        <button id="heartBtn" onclick="sendThankYouHeart()"
                            class="px-5 py-2.5 rounded-full bg-gradient-to-r from-rose-600 to-pink-600 text-white text-xs sm:text-sm font-bold shadow-lg shadow-rose-500/30 hover:scale-105 active:scale-95 transition flex items-center gap-2">
                            <span>❤️ Thả Tim Cảm Ơn</span>
                            <span id="heartCountBadge" class="px-2 py-0.5 rounded-full bg-white/20 text-xs">{{ gift.hearts }}</span>
                        </button>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <script>
        const GIFT_ID = {{ gift.id | tojson }};
        const FULL_MESSAGE = {{ gift.message | tojson }};
        const FLOWER_TYPE = {{ gift.flower_type | tojson }};

        // ==========================================
        // 1. BỘ SƯU TẬP 4 BÓ HOA SVG ĐỘC QUYỀN
        // ==========================================
        function getBouquetSVG(type) {
            const palettes = {
                rose: { main: '#e11d48', light: '#fda4af', dark: '#881337', center: '#fef08a', wrap1: '#fff1f2', wrap2: '#fecdd3' },
                tulip: { main: '#ec4899', light: '#f9a8d4', dark: '#9d174d', center: '#fde68a', wrap1: '#fdf2f8', wrap2: '#fbcfe8' },
                sunflower: { main: '#f59e0b', light: '#fde047', dark: '#78350f', center: '#451a03', wrap1: '#fffbeb', wrap2: '#fde68a' },
                peony: { main: '#db2777', light: '#fbcfe8', dark: '#831843', center: '#fef08a', wrap1: '#fff5f7', wrap2: '#f9a8d4' }
            };
            const p = palettes[type] || palettes.rose;

            return `
            <svg viewBox="0 0 360 430" class="w-full h-auto drop-shadow-2xl">
                <!-- Giấy gói Hàn Quốc lớp sau -->
                <path d="M55 170 L180 395 L305 170 Q240 120 180 140 Q120 120 55 170 Z" fill="${p.wrap2}" stroke="#fda4af" stroke-width="2"/>
                <path d="M80 150 L180 380 L280 150 Z" fill="${p.wrap1}"/>

                <!-- Lá Khuynh Diệp & Cành Xanh -->
                <g stroke="#15803d" stroke-width="4" stroke-linecap="round">
                    <path d="M180 260 L120 110"/>
                    <path d="M180 260 L240 110"/>
                    <path d="M180 260 L180 85"/>
                    <path d="M180 260 L95 160"/>
                    <path d="M180 260 L265 160"/>
                </g>
                <ellipse cx="105" cy="135" rx="18" ry="10" transform="rotate(-30 105 135)" fill="#22c55e"/>
                <ellipse cx="255" cy="135" rx="18" ry="10" transform="rotate(30 255 135)" fill="#22c55e"/>
                <ellipse cx="140" cy="95" rx="15" ry="9" transform="rotate(-15 140 95)" fill="#4ade80"/>
                <ellipse cx="220" cy="95" rx="15" ry="9" transform="rotate(15 220 95)" fill="#4ade80"/>

                <!-- 5 Bông Hoa Chính Nở Rộ -->
                ${renderBlossom(180, 105, 44, p)}
                ${renderBlossom(118, 135, 38, p)}
                ${renderBlossom(242, 135, 38, p)}
                ${renderBlossom(145, 185, 40, p)}
                ${renderBlossom(215, 185, 40, p)}

                <!-- Hoa Baby Trắng Điểm Xuyết -->
                <g fill="#ffffff" opacity="0.95">
                    <circle cx="95" cy="110" r="5"/><circle cx="108" cy="100" r="4"/>
                    <circle cx="265" cy="110" r="5"/><circle cx="252" cy="100" r="4"/>
                    <circle cx="180" cy="52" r="5"/><circle cx="165" cy="60" r="4"/><circle cx="195" cy="60" r="4"/>
                    <circle cx="110" cy="195" r="5"/><circle cx="250" cy="195" r="5"/>
                </g>

                <!-- Giấy gói lớp trước & Nơ Lụa -->
                <path d="M72 205 L180 395 L288 205 Q225 245 180 225 Q135 245 72 205 Z" fill="${p.main}" fill-opacity="0.88"/>
                <path d="M105 220 L180 395 L255 220 Q180 265 105 220 Z" fill="${p.dark}" fill-opacity="0.92"/>

                <!-- Nơ Ruy Băng Vàng Kim -->
                <path d="M180 315 C145 285 115 305 135 330 C150 342 170 325 180 315 Z" fill="#fbbf24" stroke="#fef08a" stroke-width="2"/>
                <path d="M180 315 C215 285 245 305 225 330 C210 342 190 325 180 315 Z" fill="#fbbf24" stroke="#fef08a" stroke-width="2"/>
                <path d="M172 320 L150 375 M188 320 L210 375" stroke="#f59e0b" stroke-width="6" stroke-linecap="round"/>
                <circle cx="180" cy="315" r="10" fill="#fde68a"/>
            </svg>`;
        }

        function renderBlossom(cx, cy, r, p) {
            return `
            <g transform="translate(${cx}, ${cy})">
                <circle cx="0" cy="0" r="${r}" fill="${p.dark}"/>
                <circle cx="-10" cy="-8" r="${r*0.72}" fill="${p.main}"/>
                <circle cx="10" cy="-8" r="${r*0.72}" fill="${p.main}"/>
                <circle cx="-8" cy="10" r="${r*0.72}" fill="${p.main}"/>
                <circle cx="8" cy="10" r="${r*0.72}" fill="${p.main}"/>
                <circle cx="0" cy="0" r="${r*0.58}" fill="${p.light}"/>
                <path d="M -12 -4 Q 0 -18 12 -4 Q 16 10 0 14 Q -16 10 -12 -4 Z" fill="${p.main}"/>
                <circle cx="0" cy="0" r="${r*0.24}" fill="${p.center}"/>
            </g>`;
        }

        // ==========================================
        // 2. MỞ HỘP QUÀ -> BUNG HOA -> CHẠY CHỮ
        // ==========================================
        let isOpened = false;
        function openGiftSequence() {
            if (isOpened) return;
            isOpened = true;

            playRomanticMelody();

            const box = document.getElementById('giftBox');
            const lid = document.getElementById('giftLid');
            box.classList.add('shake-box');

            setTimeout(() => {
                lid.classList.add('lid-open');
                burstHeartsAndPetals();
            }, 650);

            setTimeout(() => {
                document.getElementById('stageClosed').classList.add('hidden');
                const stageOpened = document.getElementById('stageOpened');
                stageOpened.classList.remove('hidden');

                document.getElementById('bouquetContainer').innerHTML = getBouquetSVG(FLOWER_TYPE);
                startTypewriter(FULL_MESSAGE);
            }, 1350);
        }

        function startTypewriter(text) {
            const el = document.getElementById('typewriterText');
            el.textContent = '';
            let i = 0;
            const timer = setInterval(() => {
                el.textContent += text.charAt(i);
                i++;
                if (i >= text.length) clearInterval(timer);
            }, 28);
        }

        // ==========================================
        // 3. THẢ TIM CẢM ƠN LƯU VỀ SERVER PYTHON
        // ==========================================
        async function sendThankYouHeart() {
            burstHeartsAndPetals();
            const res = await fetch(`/api/heart/${GIFT_ID}`, { method: 'POST' });
            if (res.ok) {
                const data = await res.json();
                document.getElementById('heartCountBadge').textContent = data.hearts;
            }
        }

        // ==========================================
        // 4. NHẠC HỘP (WEB AUDIO MUSIC BOX) DỊU DÀNG
        // ==========================================
        let audioCtx = null;
        let isPlayingMusic = false;
        let melodyTimer = null;

        function playRomanticMelody() {
            if (isPlayingMusic) return;
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            isPlayingMusic = true;
            document.getElementById('musicLabel').textContent = 'Đang phát nhạc';

            const notes = [523.25, 659.25, 783.99, 1046.50, 880.00, 783.99, 659.25, 587.33, 698.46, 880.00, 783.99, 659.25];
            let idx = 0;

            melodyTimer = setInterval(() => {
                if (!isPlayingMusic || !audioCtx) return;
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(notes[idx % notes.length], audioCtx.currentTime);

                gain.gain.setValueAtTime(0.001, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.11, audioCtx.currentTime + 0.04);
                gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1.1);

                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.start();
                osc.stop(audioCtx.currentTime + 1.15);
                idx++;
            }, 460);
        }

        function toggleMusic() {
            if (!isPlayingMusic) {
                playRomanticMelody();
            } else {
                isPlayingMusic = false;
                clearInterval(melodyTimer);
                document.getElementById('musicLabel').textContent = 'Đã tắt nhạc';
            }
        }

        // ==========================================
        // 5. HIỆU ỨNG MƯA CÁNH HOA & PHÁO TIM CANVAS
        // ==========================================
        const canvas = document.getElementById('petalCanvas');
        const ctx = canvas.getContext('2d');
        let particles = [];

        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        for (let i = 0; i < 36; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: 5 + Math.random() * 7,
                vx: -0.5 + Math.random() * 1,
                vy: 0.8 + Math.random() * 1.4,
                angle: Math.random() * Math.PI * 2,
                spin: -0.02 + Math.random() * 0.04,
                color: ['#fda4af', '#fb7185', '#f43f5e', '#fecdd3'][Math.floor(Math.random() * 4)],
                burst: false
            });
        }

        function burstHeartsAndPetals() {
            for (let i = 0; i < 45; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = 2 + Math.random() * 7;
                particles.push({
                    x: canvas.width / 2,
                    y: canvas.height / 2,
                    r: 6 + Math.random() * 8,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed - 2,
                    angle: Math.random() * Math.PI,
                    spin: 0.05,
                    color: ['#fbbf24', '#f43f5e', '#ec4899', '#ffe4e6'][Math.floor(Math.random() * 4)],
                    burst: true,
                    life: 90
                });
            }
        }

        function animateCanvas() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.angle += p.spin;

                if (p.burst) {
                    p.vy += 0.12;
                    p.life--;
                    if (p.life <= 0) {
                        particles.splice(i, 1);
                        continue;
                    }
                } else {
                    if (p.y > canvas.height + 20) {
                        p.y = -15;
                        p.x = Math.random() * canvas.width;
                    }
                }

                ctx.save();
                ctx.translate(p.x, p.y);
                ctx.rotate(p.angle);
                ctx.fillStyle = p.color;
                ctx.beginPath();
                ctx.ellipse(0, 0, p.r, p.r * 0.6, 0, 0, Math.PI * 2);
                ctx.fill();
                ctx.restore();
            }
            requestAnimationFrame(animateCanvas);
        }
        animateCanvas();
    </script>
</body>
</html>
"""

def ensure_templates():
    os.makedirs("templates", exist_ok=True)
    with open("templates/create.html", "w", encoding="utf-8") as f:
        f.write(CREATE_HTML)
    with open("templates/gift.html", "w", encoding="utf-8") as f:
        f.write(GIFT_HTML)

# ==========================================
# ROUTES CỦA SERVER PYTHON
# ==========================================

@app.route("/")
def index():
    """Trang 1: Studio tạo lời chúc & sinh mã QR"""
    default_base_url = get_base_url()
    return render_template("create.html", default_base_url=default_base_url)

@app.route("/qua/<gift_id>")
def view_gift(gift_id):
    """Trang 2 (Tách biệt hoàn toàn): Trang mở Hộp Quà & Hoa 3D khi quét QR"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("UPDATE gifts SET views = views + 1 WHERE id = ?", (gift_id,))
    conn.commit()
    c.execute("SELECT * FROM gifts WHERE id = ?", (gift_id,))
    row = c.fetchone()
    conn.close()

    if not row:
        abort(404, description="Không tìm thấy hộp quà 20/10 này!")
    return render_template("gift.html", gift=dict(row))

@app.route("/api/random-wish")
def api_random_wish():
    """API xoay lời chúc ngẫu nhiên theo chủ đề"""
    cat = request.args.get("category", "all")
    if cat in WISHES_DB:
        pool = WISHES_DB[cat]
    else:
        pool = [w for group in WISHES_DB.values() for w in group]
    return jsonify({"wish": secrets.choice(pool)})

@app.route("/api/create-gift", methods=["POST"])
def api_create_gift():
    """API lưu quà tặng vào SQLite và trả về mã ID ngắn cho QR"""
    data = request.get_json(force=True)
    gift_id = secrets.token_urlsafe(4).replace("-", "").replace("_", "")[:6].lower()

    sender = (data.get("sender") or "Một người luôn yêu thương bạn").strip()
    receiver = (data.get("receiver") or "Người Phụ Nữ Tuyệt Vời").strip()
    category = (data.get("category") or "all").strip()
    message = (data.get("message") or "Chúc mừng ngày Phụ nữ Việt Nam 20/10!").strip()
    flower_type = (data.get("flower_type") or "rose").strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO gifts (id, sender, receiver, category, message, flower_type, theme_color, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (gift_id, sender, receiver, category, message, flower_type, "rose", datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"id": gift_id, "url": f"/qua/{gift_id}"})

@app.route("/api/heart/<gift_id>", methods=["POST"])
def api_heart_gift(gift_id):
    """API để người nhận thả tim cảm ơn người gửi"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE gifts SET hearts = hearts + 1 WHERE id = ?", (gift_id,))
    conn.commit()
    c.execute("SELECT hearts FROM gifts WHERE id = ?", (gift_id,))
    row = c.fetchone()
    conn.close()
    return jsonify({"hearts": row[0] if row else 0})

@app.route("/api/stats/<gift_id>")
def api_stats(gift_id):
    """API kiểm tra xem người nhận đã mở quà và thả tim chưa"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT views, hearts FROM gifts WHERE id = ?", (gift_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"views": 0, "hearts": 0}), 404
    return jsonify({"views": row[0], "hearts": row[1]})

# Đảm bảo database và templates luôn được tạo khi chạy trực tiếp hoặc qua Gunicorn trên Render
init_db()
ensure_templates()

if __name__ == "__main__":
    local_ip = get_local_ip()
    ngrok_url = get_ngrok_url()
    print("=" * 60)
    print("🌷 SERVER QUÀ TẶNG & QR 20/10 ĐÃ KHỞI ĐỘNG!")
    print(f"👉 Trang Tạo Mã QR (Local)    : http://127.0.0.1:5000")
    if ngrok_url:
        print(f"👉 Link Ngrok Public (QR Link): {ngrok_url}")
    print(f"👉 Mạng LAN/Wi-Fi Nội Bộ      : http://{local_ip}:5000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=5000, debug=True)
