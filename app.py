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
# KHO LỜI CHÚC 20/10 PHONG PHÚ & CHỌN LỌC
# ==========================================
WISHES_DB = {
    "me": [
        "Nhân ngày Phụ nữ Việt Nam 20/10, con chúc Mẹ yêu luôn mạnh khỏe, bình an và mãi nở nụ cười hiền hậu. Cảm ơn Mẹ vì cả cuộc đời tần tảo hy sinh cho chúng con!",
        "20/10 chúc người phụ nữ vĩ đại nhất đời con luôn trẻ khỏe, hạnh phúc và chẳng còn những nỗi lo toan. Với con, Mẹ mãi là bầu trời bình yên nhất!",
        "Chúc Mẹ yêu ngày 20/10 ngập tràn niềm vui và hoa tươi. Mong mỗi ngày trôi qua của Mẹ đều nhẹ nhàng, an nhiên và tràn đầy tiếng cười bên gia đình mình.",
        "Không có bông hoa nào đẹp bằng nụ cười của Mẹ. Nhân ngày 20/10, con chúc Mẹ thật nhiều sức khỏe để con được chăm sóc và báo hiếu Mẹ thật lâu!",
        "Gửi ngàn lời yêu thương nhất đến Mẹ nhân ngày 20/10! Chúc Mẹ của con luôn vui vẻ, trẻ trung và mãi là điểm tựa ấm áp nhất của cả nhà.",
        "Mẹ kính yêu, con biết ơn vì từng bữa cơm, từng lời dặn dò ấm áp của Mẹ. Chúc Mẹ ngày 20/10 thật hạnh phúc, mạnh khỏe và sống đời cùng con cháu!",
        "Chúc Mẹ ngày 20/10 ngập tràn hoa thơm, mọi âu lo tan biến, chỉ còn lại niềm vui, sự thanh thản và tiếng cười rộn rã mỗi ngày!"
    ],
    "nguoi_yeu": [
        "Chúc công chúa của anh ngày 20/10 thật ngọt ngào, rạng rỡ như đóa hoa hồng buổi sớm. Cảm ơn em đã đến và làm thế giới của anh trở nên dịu dàng hơn bao giờ hết!",
        "20/10 chúc người thương của anh luôn xinh đẹp, hạnh phúc và bình yên trong vòng tay anh. Thế giới ngoài kia có bão giông thế nào thì về bên anh nhé!",
        "Gửi đến cô gái anh yêu: Chúc em ngày 20/10 ngập tràn niềm vui, luôn giữ nụ cười tỏa nắng từng làm anh rung động ngay từ lần đầu gặp gỡ.",
        "Hôm nay là 20/10, chúc em ngày càng xinh đẹp, mọi ước muốn đều thành hiện thực và mãi yêu thương anh như những ngày đầu tiên nhé!",
        "Người ta tặng hoa cho cả thế giới vào ngày 20/10, còn anh chỉ muốn gói trọn cả thế giới dịu dàng nhất dành tặng riêng cho một mình em!",
        "Em chính là món quà tuyệt vời nhất mà cuộc sống ban tặng cho anh. Chúc em ngày 20/10 thật rực rỡ, ngọt ngào và hạnh phúc trọn vẹn!",
        "Chúc em yêu ngày 20/10 vui tươi, bớt âu lo, hay ăn chóng béo và lúc nào cũng là cô gái hạnh phúc nhất trần đời bên anh!"
    ],
    "crush": [
        "Nhân ngày 20/10, chúc cậu luôn xinh đẹp, yêu đời và gặp thật nhiều may mắn. Bật mí nhỏ là nụ cười của cậu làm tim ai đó lỡ nhịp suốt đấy!",
        "20/10 chúc cô gái đáng yêu nhất hệ Mặt Trời luôn rạng rỡ như hoa hướng dương. Mong rằng những điều dịu dàng nhất sẽ luôn tìm đến bên cậu!",
        "Chúc cậu một ngày 20/10 thật đặc biệt, ngập tràn hoa và quà. Nếu hôm nay chưa có ai làm cậu cười, hy vọng món quà nhỏ này sẽ làm được điều đó!",
        "Gửi chút nắng ấm và ngàn đóa hoa nhân ngày 20/10 đến người tớ thầm thương. Chúc cậu luôn bình yên, xinh đẹp và sớm nhận ra tín hiệu từ tớ nhé!",
        "20/10 này chúc cậu nhận được thật nhiều hoa, nhưng nếu chưa có ai tặng đóa hoa đẹp nhất thì hãy nhận tấm lòng chân thành này từ tớ nhé!",
        "Hôm nay có 24 giờ, chúc cậu 20 giờ vui vẻ, 10 giờ hạnh phúc và cả ngày xinh xắn rạng ngời!",
        "Chúc bạn nữ xinh xắn đang đọc tin nhắn này có một ngày 20/10 thật ấm áp, được cưng chiều như công chúa!"
    ],
    "ban_be": [
        "Chúc các chị em bạn bè ngày 20/10 nhan sắc thăng hạng, tiền tài rực rỡ, công việc hanh thông và luôn tràn đầy năng lượng tích cực!",
        "Nhân ngày 20/10, chúc bạn tôi luôn xinh đẹp tuyệt vời, lương thưởng ngập tài khoản, deadline tự động hoàn thành và sớm có người yêu!",
        "Chúc một nửa thế giới ngày 20/10 thật tưng bừng! Mong bạn luôn tự tin, độc lập, kiêu hãnh và tỏa sáng theo cách riêng rực rỡ nhất.",
        "20/10 chúc bạn thân của tôi ăn mãi không béo, tiền tiêu không hết, ngày càng trẻ đẹp và lúc nào cũng tươi cười rạng rỡ nhé!",
        "Chúc bạn ngày 20/10 nhận quà mỏi tay, hoa ngập lối về, ăn ngon ngủ kỹ và luôn yêu đời phơi phới!",
        "Mừng 20/10 rực rỡ! Chúc bạn mãi giữ vững thần thái đỉnh chóp, độc lập tài chính và luôn là phiên bản hạnh phúc nhất của chính mình."
    ],
    "co_sep": [
        "Nhân ngày Phụ nữ Việt Nam 20/10, kính chúc Cô/Sếp luôn dồi dào sức khỏe, hạnh phúc viên mãn và gặt hái thêm nhiều thành công rực rỡ trong sự nghiệp!",
        "Gửi lời tri ân sâu sắc nhất nhân ngày 20/10. Chúc Cô/Chị luôn giữ vững ngọn lửa nhiệt huyết, trẻ trung, xinh đẹp và mãi là người truyền cảm hứng tuyệt vời!",
        "Chúc mừng ngày 20/10! Kính chúc Chị/Cô luôn rạng ngời sắc xuân, công việc thuận buồm xuôi gió và tràn ngập niềm vui bên gia đình thân yêu.",
        "Nhân ngày 20/10, em xin kính chúc Chị/Cô luôn tràn đầy nhiệt huyết, dẫn dắt tập thể gặt hái thêm nhiều thắng lợi mới và luôn tươi trẻ mỗi ngày!"
    ],
    "hai_huoc": [
        "Chúc bạn 20/10: Nhan sắc 'kịch trần', tiền tiêu 'phất phới', tình duyên 'tới tấp' và cân nặng luôn ở mức 'đỉnh của chóp'!",
        "Thông báo khẩn ngày 20/10: Chúc chị em hôm nay không phải rửa bát, không lo tăng cân, ví tiền dày cộp và nhận quà mỏi cả hai tay!",
        "20/10 chúc bạn trẻ mãi không già, sắc đẹp vượt thời gian, ví tiền vượt không gian và độ lầy lội thì không ai sánh bằng!",
        "Thay mặt Hội Đẹp Trai Toàn Cầu, chúc bạn ngày 20/10 xinh đẹp bất chấp cam thường, giàu sang bất chấp thị trường nhé!",
        "Chúc bạn ngày 20/10 sớm thoát ế, bớt thức khuya, shopping không nhìn giá và lương về ting ting liên tục!"
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

    ngrok = get_ngrok_url()
    if ngrok:
        return ngrok

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
# TRANG 1: STUDIO TẠO THIỆP & MÃ QR ĐỘNG
# ==========================================
CREATE_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Studio Tạo Thiệp & Mã QR 20/10 Cao Cấp</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Dancing+Script:wght@700&family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
    <style>
        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background: radial-gradient(circle at 10% 10%, #fff1f5 0%, #ffe4ee 40%, #fae8ff 100%);
            min-height: 100vh;
            overflow-x: hidden;
        }
        .font-serif-title { font-family: 'Playfair Display', serif; }
        .font-script { font-family: 'Dancing Script', cursive; }
        .glass-panel {
            background: rgba(255, 255, 255, 0.88);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(244, 63, 94, 0.22);
            box-shadow: 0 25px 60px rgba(190, 18, 60, 0.09);
        }
        .flower-card {
            transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        .flower-card:hover {
            transform: translateY(-4px);
        }
        .flower-card.active {
            border-color: #e11d48;
            background: linear-gradient(145deg, #ffffff 0%, #fff1f2 100%);
            box-shadow: 0 12px 25px rgba(225, 29, 72, 0.18);
            transform: translateY(-4px);
        }
        .cat-chip.active {
            background: linear-gradient(135deg, #e11d48, #be185d);
            color: white;
            border-color: transparent;
            box-shadow: 0 6px 16px rgba(225, 29, 72, 0.28);
        }
        .quick-wish-pill {
            transition: all 0.2s ease;
        }
        .quick-wish-pill:hover {
            background: #fff1f2;
            border-color: #f43f5e;
            transform: translateX(3px);
        }
        @keyframes subtleFloat {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-8px) rotate(1deg); }
        }
        .animate-float {
            animation: subtleFloat 3.8s ease-in-out infinite;
        }
    </style>
</head>
<body class="text-rose-950 py-8 px-4 sm:px-6">
    <div class="max-w-7xl mx-auto">
        <!-- Header -->
        <header class="text-center mb-10">
            <div class="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-rose-100/90 border border-rose-300 text-rose-700 text-xs font-bold tracking-widest uppercase mb-3 shadow-sm">
                🌸 Studio Tạo Thiệp & Mã QR Quà Tặng 20/10 🌸
            </div>
            <h1 class="font-serif-title text-3xl sm:text-5xl lg:text-6xl font-bold text-rose-950 mb-3">
                Thiết Kế Hộp Quà & Mã QR <span class="text-transparent bg-clip-text bg-gradient-to-r from-rose-600 via-pink-600 to-amber-600 italic">20/10</span>
            </h1>
            <p class="text-rose-800/80 max-w-3xl mx-auto text-sm sm:text-base leading-relaxed">
                Tự động đồng bộ nội dung QR và lời chúc theo thời gian thực. Bó hoa được thiết kế riêng biệt từng loài (<b>Hoa Hồng, Tulip, Hướng Dương, Mẫu Đơn</b>). Người nhận quét mã sẽ mở ngay trang <b>Hộp Quà & Bó Hoa 3D</b> sống động!
            </p>
        </header>

        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
            <!-- CỘT TRÁI: FORM CẤU HÌNH QUÀ & LỜI CHÚC -->
            <div class="lg:col-span-7 glass-panel rounded-3xl p-6 sm:p-8 space-y-6">
                <div class="flex items-center justify-between pb-4 border-b border-rose-100">
                    <div>
                        <h2 class="font-serif-title text-2xl font-bold text-rose-900 flex items-center gap-2">
                            <span>1. Tùy Chỉnh Lời Chúc & Loài Hoa</span>
                        </h2>
                        <p class="text-xs text-rose-600/80">Mọi thay đổi sẽ tự động cập nhật ngay lập tức vào Mã QR</p>
                    </div>
                    <div id="syncBadge" class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300 shadow-sm transition-all">
                        <span class="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                        <span>Đã đồng bộ QR</span>
                    </div>
                </div>

                <!-- Tên người nhận & người gửi -->
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-rose-800 mb-1.5 flex items-center gap-1.5">
                            <span>👑 Dành tặng cho (Người nhận)</span>
                        </label>
                        <input id="receiverInput" type="text" value="Người Phụ Nữ Tuyệt Vời" placeholder="VD: Mẹ yêu, Em yêu, Thu Hà..."
                            class="w-full px-4 py-3 rounded-2xl border border-rose-200 bg-white/95 focus:outline-none focus:ring-2 focus:ring-rose-500 font-semibold text-sm shadow-sm transition">
                    </div>
                    <div>
                        <label class="block text-xs font-bold uppercase tracking-wider text-rose-800 mb-1.5 flex items-center gap-1.5">
                            <span>💌 Từ (Người gửi)</span>
                        </label>
                        <input id="senderInput" type="text" value="Một người luôn yêu thương bạn" placeholder="VD: Con trai của Mẹ, Anh..."
                            class="w-full px-4 py-3 rounded-2xl border border-rose-200 bg-white/95 focus:outline-none focus:ring-2 focus:ring-rose-500 font-semibold text-sm shadow-sm transition">
                    </div>
                </div>

                <!-- 4 LOẠI HOA VẼ RIÊNG BIỆT (TULIP, HƯỚNG DƯƠNG, MẪU ĐƠN, HOA HỒNG) -->
                <div>
                    <div class="flex items-center justify-between mb-2">
                        <label class="text-xs font-bold uppercase tracking-wider text-rose-800">
                            💐 Chọn Loài Hoa 3D Trong Hộp Quà (Hình Dáng Riêng Biệt)
                        </label>
                        <span id="flowerBadge" class="text-[11px] font-bold text-rose-600 bg-rose-50 px-2.5 py-0.5 rounded-full border border-rose-200">
                            Hồng Nhung Đỏ
                        </span>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-4 gap-3" id="flowerSelector">
                        <!-- Hoa Hồng -->
                        <div data-flower="rose" class="flower-card active cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3.5 text-center shadow-sm">
                            <div class="text-3xl mb-1">🌹</div>
                            <div class="text-xs font-bold text-rose-950">Hồng Nhung Đỏ</div>
                            <div class="text-[10px] text-rose-600 font-medium mt-0.5">Xoáy cánh kiêu sa</div>
                        </div>

                        <!-- Tulip -->
                        <div data-flower="tulip" class="flower-card cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3.5 text-center shadow-sm">
                            <div class="text-3xl mb-1">🌷</div>
                            <div class="text-xs font-bold text-rose-950">Tulip Hà Lan</div>
                            <div class="text-[10px] text-pink-600 font-medium mt-0.5">Búp chuông thanh thuần</div>
                        </div>

                        <!-- Hướng Dương -->
                        <div data-flower="sunflower" class="flower-card cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3.5 text-center shadow-sm">
                            <div class="text-3xl mb-1">🌻</div>
                            <div class="text-xs font-bold text-rose-950">Hướng Dương</div>
                            <div class="text-[10px] text-amber-600 font-medium mt-0.5">Tia nắng rạng ngời</div>
                        </div>

                        <!-- Mẫu Đơn -->
                        <div data-flower="peony" class="flower-card cursor-pointer rounded-2xl border-2 border-rose-200 bg-white p-3.5 text-center shadow-sm">
                            <div class="text-3xl mb-1">🌺</div>
                            <div class="text-xs font-bold text-rose-950">Mẫu Đơn Hoàng Gia</div>
                            <div class="text-[10px] text-fuchsia-600 font-medium mt-0.5">Tầng tầng cánh dập dờn</div>
                        </div>
                    </div>
                </div>

                <!-- CHỦ ĐỀ VÀ LỜI CHÚC PHONG PHÚ -->
                <div>
                    <div class="flex flex-wrap items-center justify-between gap-2 mb-2.5">
                        <label class="text-xs font-bold uppercase tracking-wider text-rose-800">
                            📝 Lời Chúc 20/10 Theo Chủ Đề
                        </label>
                        <button type="button" onclick="fetchRandomWish()"
                            class="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-gradient-to-r from-amber-500 to-rose-600 text-white text-xs font-bold shadow-md hover:brightness-105 active:scale-95 transition">
                            🎲 Đổi Lời Chúc Ngẫu Nhiên
                        </button>
                    </div>

                    <!-- Category Chips -->
                    <div class="flex flex-wrap gap-2 mb-3" id="categoryChips">
                        <button type="button" data-cat="all" class="cat-chip active px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">✨ Tất cả</button>
                        <button type="button" data-cat="me" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">🌷 Mẹ yêu</button>
                        <button type="button" data-cat="nguoi_yeu" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">❤️ Vợ / Người yêu</button>
                        <button type="button" data-cat="crush" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">💌 Crush</button>
                        <button type="button" data-cat="ban_be" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">🥂 Bạn bè</button>
                        <button type="button" data-cat="co_sep" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">💐 Cô giáo / Sếp</button>
                        <button type="button" data-cat="hai_huoc" class="cat-chip px-3 py-1.5 rounded-full border border-rose-200 bg-white text-xs font-semibold transition">😂 Hài hước</button>
                    </div>

                    <!-- Textarea nhập lời chúc -->
                    <textarea id="messageInput" rows="4"
                        class="w-full px-4 py-3 rounded-2xl border border-rose-200 bg-white/95 focus:outline-none focus:ring-2 focus:ring-rose-500 text-sm leading-relaxed shadow-sm transition"
                        placeholder="Nhập lời chúc 20/10 ngọt ngào của riêng bạn hoặc chọn từ danh sách gợi ý bên dưới...">Nhân ngày Phụ nữ Việt Nam 20/10, chúc bạn luôn xinh đẹp rạng ngời như những đóa hoa tươi thắm, ngập tràn niềm vui, sức khỏe dồi dào và hạnh phúc viên mãn trọn vẹn!</textarea>

                    <!-- Gợi ý danh sách lời chúc bấm chọn nhanh -->
                    <div class="mt-2.5">
                        <span class="text-[11px] font-bold text-rose-700 uppercase tracking-wider block mb-1.5">
                            💡 Gợi ý câu chúc hay (Bấm để chọn ngay):
                        </span>
                        <div id="quickWishesList" class="max-h-36 overflow-y-auto space-y-1.5 pr-1"></div>
                    </div>
                </div>

                <!-- Cấu hình Domain Server (Tự động nhận Render / Ngrok) -->
                <div class="p-4 rounded-2xl bg-rose-50/80 border border-rose-200/80">
                    <div class="flex items-center justify-between mb-1">
                        <label class="block text-[11px] font-bold uppercase tracking-wider text-rose-800">
                            🌐 Địa chỉ Server tạo QR (Tự động nhận diện Render / Ngrok)
                        </label>
                        <span class="text-[10px] bg-rose-600 text-white font-bold px-2 py-0.5 rounded-full shadow-sm">Online Ready</span>
                    </div>
                    <input id="baseUrlInput" type="text" value="{{ default_base_url }}"
                        class="w-full px-3 py-2 rounded-xl border border-rose-200 bg-white text-xs font-mono text-rose-900 focus:outline-none focus:ring-2 focus:ring-rose-400">
                    <p class="text-[11px] text-rose-600/80 mt-1">💡 Link này được nạp vào Mã QR. Khi quét trên điện thoại (4G / Wi-Fi) sẽ mở thẳng trang quà tặng.</p>
                </div>

                <!-- Các nút hành động -->
                <div class="flex flex-wrap sm:flex-nowrap gap-3 pt-2">
                    <button type="button" onclick="createNewGiftFresh()"
                        class="w-full sm:w-1/2 py-3.5 px-4 rounded-2xl bg-white border-2 border-rose-300 text-rose-800 hover:bg-rose-50 font-bold text-sm shadow-sm transition flex items-center justify-center gap-2">
                        <span>✨ Tạo Mã / Thiệp Mới</span>
                    </button>
                    <button type="button" onclick="syncGift(true)"
                        class="w-full sm:w-1/2 py-3.5 px-4 rounded-2xl bg-gradient-to-r from-rose-600 via-pink-600 to-rose-500 text-white font-bold text-sm shadow-lg shadow-rose-500/25 hover:brightness-105 active:scale-[0.99] transition flex items-center justify-center gap-2">
                        <span>🚀 Cập Nhật & Lưu Ngay</span>
                    </button>
                </div>
            </div>

            <!-- CỘT PHẢI: XEM TRƯỚC BÓ HOA 3D & THẺ POSTER QR -->
            <div class="lg:col-span-5 space-y-6 sticky top-6">
                <!-- XEM TRƯỚC BÓ HOA ĐANG CHỌN -->
                <div class="glass-panel rounded-3xl p-5 text-center">
                    <div class="flex items-center justify-between mb-2 pb-2 border-b border-rose-100">
                        <span class="text-xs font-bold uppercase tracking-wider text-rose-700">💐 Bó Hoa Xem Trước</span>
                        <span id="previewFlowerName" class="text-xs font-bold text-rose-800 bg-rose-100 px-2.5 py-0.5 rounded-full">Hoa Hồng</span>
                    </div>

                    <div id="studioBouquetPreview" class="w-56 h-56 mx-auto flex items-center justify-center animate-float"></div>

                    <p id="flowerMeaningText" class="text-xs text-rose-700/90 italic font-medium mt-2 bg-rose-50/70 py-2 px-3 rounded-xl border border-rose-200/50">
                        "Biểu tượng của tình yêu nồng nàn, sự trân trọng và vẻ đẹp kiêu sa vượt thời gian."
                    </p>
                </div>

                <!-- THẺ POSTER QR ĐẲNG CẤP -->
                <div class="glass-panel rounded-3xl p-6 text-center">
                    <h3 class="font-serif-title text-2xl font-bold text-rose-900 mb-1">Thẻ Quét QR Quà Tặng</h3>
                    <p class="text-xs text-rose-600/80 mb-4">Quét bằng Camera điện thoại hoặc Zalo để mở Hộp Quà 3D</p>

                    <div id="qrPosterCard" class="mx-auto max-w-xs rounded-3xl p-5 border-2 border-rose-200 shadow-lg relative overflow-hidden"
                         style="background: linear-gradient(165deg, #fff5f7 0%, #ffe4ec 100%);">
                        <div class="text-[11px] font-bold tracking-widest uppercase text-rose-500 mb-1">HAPPY WOMEN'S DAY 20/10</div>
                        <div id="posterReceiver" class="font-script text-3xl text-rose-800 mb-3 truncate">Người Phụ Nữ Tuyệt Vời</div>

                        <!-- Khung chứa QR -->
                        <div class="bg-white p-3.5 rounded-2xl shadow-md inline-block border border-rose-100 mx-auto mb-3">
                            <div id="qrcodeContainer" class="flex items-center justify-center min-h-[190px] min-w-[190px]"></div>
                        </div>

                        <p class="text-xs font-bold text-rose-800">📱 Quét mã để mở Hộp Quà & Bó Hoa 3D</p>
                        <p id="posterSender" class="text-[11px] text-rose-600 mt-1 italic">Từ: Một người luôn yêu thương bạn</p>
                    </div>

                    <!-- Link trang quà & các nút tải/xem -->
                    <div id="giftLinkBox" class="mt-4 space-y-3">
                        <div class="flex items-center gap-2">
                            <input id="shortUrlOutput" readonly type="text"
                                class="w-full px-3 py-2.5 rounded-xl bg-white border border-rose-200 text-xs font-mono text-rose-900 shadow-sm">
                            <button onclick="copyGiftUrl()" class="px-3.5 py-2.5 rounded-xl bg-rose-100 hover:bg-rose-200 text-rose-800 text-xs font-bold shrink-0 transition">
                                Copy
                            </button>
                        </div>

                        <div class="grid grid-cols-2 gap-2.5">
                            <a id="openGiftPageBtn" href="#" target="_blank"
                                class="py-3 px-3 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold shadow-md transition flex items-center justify-center gap-1.5">
                                🎁 Xem Thử Mở Quà
                            </a>
                            <button onclick="downloadPosterPNG()"
                                class="py-3 px-3 rounded-xl bg-amber-500 hover:bg-amber-600 text-white text-xs font-bold shadow-md transition flex items-center justify-center gap-1.5">
                                📥 Tải Ảnh QR (PNG)
                            </button>
                        </div>

                        <!-- Thống kê lượt xem và tim -->
                        <div class="p-2.5 rounded-xl bg-white/80 border border-rose-100 flex items-center justify-around text-xs">
                            <div>
                                <span class="text-rose-500">👁️ Lượt xem:</span>
                                <b id="statViews" class="text-rose-900 ml-1">0</b>
                            </div>
                            <div class="h-3.5 w-px bg-rose-200"></div>
                            <div>
                                <span class="text-rose-500">❤️ Thả tim:</span>
                                <b id="statHearts" class="text-rose-600 ml-1">0</b>
                            </div>
                            <button onclick="refreshStats()" class="text-[11px] text-rose-600 underline font-semibold">Làm mới</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- SCRIPT TỰ ĐỘNG SYNC, VẼ 4 LOÀI HOA RIÊNG BIỆT & RENDER QR -->
    <script>
        let selectedCategory = 'all';
        let selectedFlower = 'rose';
        let currentGiftId = null;
        let currentGiftUrl = '';
        let syncTimeout = null;

        const FLOWER_INFO = {
            rose: {
                name: 'Hoa Hồng Nhung Đỏ',
                meaning: 'Biểu tượng của tình yêu nồng nàn, sự trân trọng và vẻ đẹp kiêu sa vượt thời gian.'
            },
            tulip: {
                name: 'Bó Hoa Tulip Hà Lan',
                meaning: 'Biểu tượng của sự duyên dáng, thanh khiết và lời chúc an yên, ngọt ngào.'
            },
            sunflower: {
                name: 'Bó Hoa Hướng Dương',
                meaning: 'Luôn hướng về ánh dương - biểu tượng của niềm tin, sự lạc quan và ấm áp rực rỡ.'
            },
            peony: {
                name: 'Bó Hoa Mẫu Đơn Hoàng Gia',
                meaning: 'Quốc sắc thiên hương - biểu tượng của sự vương giả, thịnh vượng và hạnh phúc viên mãn.'
            }
        };

        // ==========================================
        // VẼ 4 LOÀI HOA KHÁC BIỆT HOÀN TOÀN (SVG)
        // ==========================================
        function generateBouquetSVG(type) {
            if (type === 'tulip') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-xl">
                    <defs>
                        <linearGradient id="tWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fce7f3"/></linearGradient>
                        <linearGradient id="tWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f472b6"/><stop offset="100%" stop-color="#db2777"/></linearGradient>
                        <linearGradient id="tPetal1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f43f5e"/><stop offset="70%" stop-color="#ec4899"/><stop offset="100%" stop-color="#ffe4e6"/></linearGradient>
                        <linearGradient id="tPetal2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#fb7185"/><stop offset="60%" stop-color="#f472b6"/><stop offset="100%" stop-color="#fff1f2"/></linearGradient>
                        <linearGradient id="tLeaf" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4ade80"/><stop offset="100%" stop-color="#15803d"/></linearGradient>
                    </defs>
                    <!-- Giấy gói hoa tulip lớp sau -->
                    <path d="M70 190 L190 435 L310 190 Q250 140 190 160 Q130 140 70 190 Z" fill="url(#tWrap1)" stroke="#f472b6" stroke-width="2"/>
                    <path d="M100 170 L190 415 L280 170 Z" fill="#ffffff" fill-opacity="0.85"/>

                    <!-- Lá Tulip thon dài cong vút mềm mại đặc trưng -->
                    <path d="M190 290 Q120 200 100 95 Q145 155 185 245 Z" fill="url(#tLeaf)" opacity="0.95"/>
                    <path d="M190 290 Q260 200 280 95 Q235 155 195 245 Z" fill="url(#tLeaf)" opacity="0.95"/>
                    <path d="M190 290 Q70 230 65 140 Q110 190 180 260 Z" fill="#22c55e" opacity="0.9"/>
                    <path d="M190 290 Q310 230 315 140 Q270 190 200 260 Z" fill="#22c55e" opacity="0.9"/>
                    <path d="M190 280 Q190 170 190 65 Q200 150 190 250 Z" fill="#16a34a" stroke="#15803d" stroke-width="1.5"/>

                    <!-- Cành hoa -->
                    <path d="M190 310 L190 120" stroke="#15803d" stroke-width="6" stroke-linecap="round"/>
                    <path d="M190 310 L135 155" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L245 155" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L95 195" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L285 195" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>

                    <!-- 5 Bông Tulip Dáng Chuông Kiêu Kỳ -->
                    <g transform="translate(190, 110)">
                        <path d="M -16 10 C -22 -20 -15 -55 0 -65 C 15 -55 22 -20 16 10 Z" fill="url(#tPetal1)"/>
                        <path d="M -24 15 C -30 -15 -18 -45 -6 -52 C -12 -15 0 10 -24 15 Z" fill="url(#tPetal2)"/>
                        <path d="M 24 15 C 30 -15 18 -45 6 -52 C 12 -15 0 10 24 15 Z" fill="url(#tPetal2)"/>
                        <ellipse cx="0" cy="5" rx="8" ry="4" fill="#fbcfe8" opacity="0.7"/>
                    </g>
                    <g transform="translate(135, 145) rotate(-14)">
                        <path d="M -15 10 C -20 -18 -14 -50 0 -60 C 14 -50 20 -18 15 10 Z" fill="url(#tPetal1)"/>
                        <path d="M -22 14 C -28 -12 -16 -40 -5 -48 C -10 -12 0 10 -22 14 Z" fill="url(#tPetal2)"/>
                        <path d="M 22 14 C 28 -12 16 -40 5 -48 C 10 -12 0 10 22 14 Z" fill="url(#tPetal2)"/>
                    </g>
                    <g transform="translate(245, 145) rotate(14)">
                        <path d="M -15 10 C -20 -18 -14 -50 0 -60 C 14 -50 20 -18 15 10 Z" fill="url(#tPetal1)"/>
                        <path d="M -22 14 C -28 -12 -16 -40 -5 -48 C -10 -12 0 10 -22 14 Z" fill="url(#tPetal2)"/>
                        <path d="M 22 14 C 28 -12 16 -40 5 -48 C 10 -12 0 10 22 14 Z" fill="url(#tPetal2)"/>
                    </g>
                    <g transform="translate(95, 190) rotate(-22)">
                        <path d="M -14 8 C -18 -15 -12 -42 0 -52 C 12 -42 18 -15 14 8 Z" fill="url(#tPetal1)"/>
                        <path d="M -20 12 C -25 -10 -14 -35 -4 -42 C -9 -10 0 8 -20 12 Z" fill="url(#tPetal2)"/>
                        <path d="M 20 12 C 25 -10 14 -35 4 -42 C 9 -10 0 8 20 12 Z" fill="url(#tPetal2)"/>
                    </g>
                    <g transform="translate(285, 190) rotate(22)">
                        <path d="M -14 8 C -18 -15 -12 -42 0 -52 C 12 -42 18 -15 14 8 Z" fill="url(#tPetal1)"/>
                        <path d="M -20 12 C -25 -10 -14 -35 -4 -42 C -9 -10 0 8 -20 12 Z" fill="url(#tPetal2)"/>
                        <path d="M 20 12 C 25 -10 14 -35 4 -42 C 9 -10 0 8 20 12 Z" fill="url(#tPetal2)"/>
                    </g>

                    <!-- Giấy gói lớp trước và nơ satin -->
                    <path d="M85 220 L190 435 L295 220 Q240 260 190 240 Q140 260 85 220 Z" fill="url(#tWrap2)" opacity="0.95"/>
                    <path d="M120 235 L190 435 L260 235 Q190 270 120 235 Z" fill="#be185d" opacity="0.9"/>
                    <!-- Nơ satin hồng phấn -->
                    <path d="M190 335 C150 305 120 325 140 350 C155 362 180 345 190 335 Z" fill="#f472b6" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M190 335 C230 305 260 325 240 350 C225 362 200 345 190 335 Z" fill="#f472b6" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M182 340 L160 405 M198 340 L220 405" stroke="#ec4899" stroke-width="6" stroke-linecap="round"/>
                    <circle cx="190" cy="335" r="10" fill="#fff1f2" stroke="#f472b6" stroke-width="3"/>
                </svg>`;
            } else if (type === 'sunflower') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-xl">
                    <defs>
                        <linearGradient id="sWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fef9c3"/><stop offset="100%" stop-color="#fef08a"/></linearGradient>
                        <linearGradient id="sWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#b45309"/><stop offset="100%" stop-color="#78350f"/></linearGradient>
                        <radialGradient id="sCenter" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#2a1202"/><stop offset="65%" stop-color="#451a03"/><stop offset="100%" stop-color="#a16207"/></radialGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#sWrap1)" stroke="#d97706" stroke-width="2"/>
                    <path d="M90 160 L190 415 L290 160 Z" fill="#fef08a" opacity="0.6"/>

                    <!-- Cành lá to bản xanh đậm -->
                    <g stroke="#15803d" stroke-width="5" stroke-linecap="round">
                        <path d="M190 280 L190 115"/>
                        <path d="M190 280 L125 180"/>
                        <path d="M190 280 L255 180"/>
                    </g>
                    <path d="M140 230 Q90 180 80 130 Q120 160 150 210 Z" fill="#15803d"/>
                    <path d="M240 230 Q290 180 300 130 Q260 160 230 210 Z" fill="#15803d"/>
                    <path d="M190 220 Q160 170 150 120 Q180 150 190 200 Z" fill="#16a34a"/>
                    <path d="M190 220 Q220 170 230 120 Q200 150 190 200 Z" fill="#16a34a"/>

                    <!-- 3 Bông Hướng Dương Với Cánh Tỏa Tia & Nhụy Hạt -->
                    ${renderSunflowerSVG(190, 110, 52)}
                    ${renderSunflowerSVG(125, 180, 44)}
                    ${renderSunflowerSVG(255, 180, 44)}

                    <!-- Cúc họa mi nhỏ phụ trợ -->
                    <g fill="#ffffff" stroke="#fef08a" stroke-width="1.5">
                        <circle cx="85" cy="140" r="7"/><circle cx="85" cy="140" r="3" fill="#eab308"/>
                        <circle cx="295" cy="140" r="7"/><circle cx="295" cy="140" r="3" fill="#eab308"/>
                        <circle cx="190" cy="45" r="8"/><circle cx="190" cy="45" r="3" fill="#eab308"/>
                    </g>

                    <path d="M80 210 L190 435 L300 210 Q240 255 190 235 Q140 255 80 210 Z" fill="url(#sWrap2)" opacity="0.95"/>
                    <path d="M110 225 L190 435 L270 225 Q190 270 110 225 Z" fill="#451a03" opacity="0.9"/>
                    <!-- Nơ ruy băng vàng cam -->
                    <path d="M190 330 C150 295 115 315 135 345 C150 360 175 340 190 330 Z" fill="#f59e0b" stroke="#fef08a" stroke-width="2"/>
                    <path d="M190 330 C230 295 265 315 245 345 C230 360 205 340 190 330 Z" fill="#f59e0b" stroke="#fef08a" stroke-width="2"/>
                    <path d="M182 335 L160 405 M198 335 L220 405" stroke="#d97706" stroke-width="6" stroke-linecap="round"/>
                    <circle cx="190" cy="330" r="10" fill="#fef08a" stroke="#d97706" stroke-width="3"/>
                </svg>`;
            } else if (type === 'peony') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-xl">
                    <defs>
                        <linearGradient id="pWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fce7f3"/></linearGradient>
                        <linearGradient id="pWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f472b6"/><stop offset="100%" stop-color="#9d174d"/></linearGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#pWrap1)" stroke="#f472b6" stroke-width="2"/>
                    <path d="M90 160 L190 415 L290 160 Z" fill="#ffffff" opacity="0.8"/>

                    <!-- Cành lá bạch đàn (Eucalyptus) sang chảnh -->
                    <g fill="#64748b" opacity="0.75">
                        <ellipse cx="95" cy="115" rx="15" ry="10" transform="rotate(-30 95 115)"/>
                        <ellipse cx="120" cy="85" rx="15" ry="11" transform="rotate(-15 120 85)"/>
                        <ellipse cx="285" cy="115" rx="15" ry="10" transform="rotate(30 285 115)"/>
                        <ellipse cx="260" cy="85" rx="15" ry="11" transform="rotate(15 260 85)"/>
                        <ellipse cx="190" cy="50" rx="16" ry="11"/>
                    </g>
                    <path d="M190 280 L190 120" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L130 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L250 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>

                    <!-- 4 Bông Mẫu Đơn Tầng Tầng Cánh Dập Dờn Bồng Bềnh -->
                    ${renderPeonySVG(190, 115, 50)}
                    ${renderPeonySVG(125, 175, 42)}
                    ${renderPeonySVG(255, 175, 42)}
                    ${renderPeonySVG(190, 205, 44)}

                    <path d="M80 215 L190 435 L300 215 Q240 260 190 240 Q140 260 80 215 Z" fill="url(#pWrap2)" opacity="0.95"/>
                    <path d="M115 230 L190 435 L265 230 Q190 275 115 230 Z" fill="#831843" opacity="0.9"/>
                    <!-- Nơ lụa voan hồng đào -->
                    <path d="M190 335 C150 300 115 320 135 350 C150 365 175 345 190 335 Z" fill="#db2777" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M190 335 C230 300 265 320 245 350 C230 365 205 345 190 335 Z" fill="#db2777" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M182 340 L160 410 M198 340 L220 410" stroke="#be185d" stroke-width="6" stroke-linecap="round"/>
                    <circle cx="190" cy="335" r="10" fill="#fff1f2" stroke="#db2777" stroke-width="3"/>
                </svg>`;
            } else {
                // Mặc định: Hoa Hồng Nhung Đỏ (Rose)
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-xl">
                    <defs>
                        <linearGradient id="rWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fecdd3"/></linearGradient>
                        <linearGradient id="rWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#be123c"/><stop offset="100%" stop-color="#881337"/></linearGradient>
                        <linearGradient id="rGold" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fef08a"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/></linearGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#rWrap1)" stroke="#fda4af" stroke-width="2"/>
                    <path d="M90 160 L190 415 L290 160 Z" fill="#ffffff" opacity="0.8"/>

                    <!-- Lá hoa hồng xanh thẫm viền răng cưa -->
                    <g fill="#166534">
                        <path d="M120 140 Q80 120 70 90 Q105 105 125 130 Z"/>
                        <path d="M260 140 Q300 120 310 90 Q275 105 255 130 Z"/>
                        <path d="M150 90 Q120 60 110 30 Q140 50 155 80 Z"/>
                        <path d="M230 90 Q260 60 270 30 Q240 50 225 80 Z"/>
                    </g>
                    <path d="M190 280 L190 120" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L125 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L255 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>

                    <!-- 5 Đóa Hoa Hồng Nhung Đỏ Xoáy Cánh 3D Kiêu Sa -->
                    ${renderRoseSVG(190, 110, 48)}
                    ${renderRoseSVG(120, 160, 42)}
                    ${renderRoseSVG(260, 160, 42)}
                    ${renderRoseSVG(150, 205, 40)}
                    ${renderRoseSVG(230, 205, 40)}

                    <!-- Hoa Baby Trắng Điểm Xuyết Mây Bồng -->
                    <g fill="#ffffff" opacity="0.95">
                        <circle cx="85" cy="115" r="5"/><circle cx="98" cy="105" r="4"/><circle cx="75" cy="130" r="4.5"/>
                        <circle cx="295" cy="115" r="5"/><circle cx="282" cy="105" r="4"/><circle cx="305" cy="130" r="4.5"/>
                        <circle cx="190" cy="48" r="5"/><circle cx="175" cy="55" r="4"/><circle cx="205" cy="55" r="4"/>
                        <circle cx="105" cy="180" r="5"/><circle cx="275" cy="180" r="5"/>
                    </g>

                    <path d="M80 215 L190 435 L300 215 Q240 260 190 240 Q140 260 80 215 Z" fill="url(#rWrap2)" opacity="0.95"/>
                    <path d="M115 230 L190 435 L265 230 Q190 275 115 230 Z" fill="#4c0519" opacity="0.9"/>
                    <!-- Nơ ruy băng vàng kim -->
                    <path d="M190 335 C150 300 115 320 135 350 C150 365 175 345 190 335 Z" fill="url(#rGold)" stroke="#fef08a" stroke-width="2"/>
                    <path d="M190 335 C230 300 265 320 245 350 C230 365 205 345 190 335 Z" fill="url(#rGold)" stroke="#fef08a" stroke-width="2"/>
                    <path d="M182 340 L160 410 M198 340 L220 410" stroke="#f59e0b" stroke-width="6" stroke-linecap="round"/>
                    <circle cx="190" cy="335" r="10" fill="#fef08a" stroke="#d97706" stroke-width="3"/>
                </svg>`;
            }
        }

        // Helper render đóa hoa hồng đỏ xoáy cánh
        function renderRoseSVG(cx, cy, r) {
            return `
            <g transform="translate(${cx}, ${cy})">
                <!-- Cánh ngoài bung xòe -->
                <circle cx="0" cy="0" r="${r}" fill="#881337"/>
                <path d="M ${-r} 0 C ${-r*1.1} ${-r*0.8} ${-r*0.2} ${-r*1.1} 0 ${-r*0.9} C ${r*0.6} ${-r*1.1} ${r} ${-r*0.6} ${r} 0 C ${r*1.1} ${r*0.7} 0 ${r*1.1} ${-r} 0 Z" fill="#9f1239"/>
                <path d="M ${-r*0.75} ${-r*0.5} C ${-r*0.9} ${r*0.3} ${-r*0.2} ${r*0.9} ${r*0.5} ${r*0.7} C ${r*0.9} ${r*0.1} ${r*0.7} ${-r*0.7} ${-r*0.75} ${-r*0.5} Z" fill="#be123c"/>
                <path d="M ${-r*0.5} ${r*0.4} C ${-r*0.7} ${-r*0.5} ${r*0.2} ${-r*0.8} ${r*0.6} ${-r*0.3} C ${r*0.8} ${r*0.5} ${-r*0.1} ${r*0.8} ${-r*0.5} ${r*0.4} Z" fill="#e11d48"/>
                <!-- Tâm xoáy ốc -->
                <path d="M ${-r*0.35} ${-r*0.2} C ${-r*0.5} ${r*0.2} ${r*0.1} ${r*0.5} ${r*0.4} ${r*0.1} C ${r*0.5} ${-r*0.4} ${-r*0.1} ${-r*0.5} ${-r*0.35} ${-r*0.2} Z" fill="#f43f5e"/>
                <ellipse cx="0" cy="0" rx="${r*0.22}" ry="${r*0.16}" fill="#fb7185"/>
                <ellipse cx="0" cy="0" rx="${r*0.12}" ry="${r*0.08}" fill="#ffe4e6"/>
            </g>`;
        }

        // Helper render bông hướng dương tỏa tia 18 cánh
        function renderSunflowerSVG(cx, cy, r) {
            let petals = '';
            for (let i = 0; i < 18; i++) {
                const deg = i * 20;
                petals += `<path d="M 0 0 C -7 -${r*0.4} -5 -${r*0.9} 0 -${r} C 5 -${r*0.9} 7 -${r*0.4} 0 0 Z" transform="rotate(${deg})" fill="${i % 2 === 0 ? '#f59e0b' : '#facc15'}"/>`;
            }
            return `
            <g transform="translate(${cx}, ${cy})">
                ${petals}
                <!-- Tâm nhụy to hạt tròn -->
                <circle cx="0" cy="0" r="${r*0.48}" fill="url(#sCenter)"/>
                <circle cx="0" cy="0" r="${r*0.4}" fill="#2a1202" opacity="0.9"/>
                <circle cx="0" cy="0" r="${r*0.25}" fill="#451a03"/>
                <circle cx="0" cy="0" r="${r*0.1}" fill="#78350f"/>
            </g>`;
        }

        // Helper render hoa mẫu đơn tầng tầng cánh lượn sóng
        function renderPeonySVG(cx, cy, r) {
            return `
            <g transform="translate(${cx}, ${cy})">
                <circle cx="0" cy="0" r="${r}" fill="#9d174d"/>
                <!-- Tầng cánh ngoài bèo nhún -->
                <path d="M ${-r} 0 C ${-r} ${-r*0.8} ${-r*0.3} ${-r*1.05} 0 ${-r*0.95} C ${r*0.4} ${-r*1.05} ${r} ${-r*0.7} ${r} 0 C ${r*1.05} ${r*0.8} 0 ${r*1.05} ${-r} 0 Z" fill="#be185d"/>
                <path d="M ${-r*0.85} ${-r*0.3} C ${-r*0.8} ${r*0.7} ${r*0.3} ${r*0.85} ${r*0.7} ${r*0.4} C ${r*0.85} ${-r*0.5} ${-r*0.3} ${-r*0.8} ${-r*0.85} ${-r*0.3} Z" fill="#db2777"/>
                <!-- Tầng cánh giữa -->
                <path d="M ${-r*0.65} ${r*0.2} C ${-r*0.7} ${-r*0.5} ${r*0.1} ${-r*0.7} ${r*0.55} ${-r*0.2} C ${r*0.65} ${r*0.5} ${-r*0.2} ${r*0.7} ${-r*0.65} ${r*0.2} Z" fill="#ec4899"/>
                <path d="M ${-r*0.45} ${-r*0.2} C ${-r*0.4} ${r*0.4} ${r*0.3} ${r*0.45} ${r*0.45} ${-r*0.1} C ${r*0.4} ${-r*0.4} ${-r*0.2} ${-r*0.45} ${-r*0.45} ${-r*0.2} Z" fill="#f472b6"/>
                <!-- Lớp cánh trong & nhụy vàng hoàng gia -->
                <circle cx="0" cy="0" r="${r*0.26}" fill="#fbcfe8"/>
                <circle cx="-2" cy="-2" r="${r*0.14}" fill="#fdf2f8"/>
                <circle cx="2" cy="1" r="${r*0.1}" fill="#fbbf24"/>
                <circle cx="-3" cy="2" r="${r*0.07}" fill="#f59e0b"/>
                <circle cx="1" cy="-3" r="${r*0.07}" fill="#fde68a"/>
            </g>`;
        }

        // ==========================================
        // CẬP NHẬT GIAO DIỆN XEM TRƯỚC BÓ HOA
        // ==========================================
        function updateFlowerPreview() {
            const previewEl = document.getElementById('studioBouquetPreview');
            const nameEl = document.getElementById('previewFlowerName');
            const badgeEl = document.getElementById('flowerBadge');
            const meaningEl = document.getElementById('flowerMeaningText');

            const info = FLOWER_INFO[selectedFlower] || FLOWER_INFO.rose;
            previewEl.innerHTML = generateBouquetSVG(selectedFlower);
            nameEl.textContent = info.name;
            badgeEl.textContent = info.name;
            meaningEl.textContent = `"${info.meaning}"`;
        }

        // ==========================================
        // TẢI DANH SÁCH LỜI CHÚC CHO CHỦ ĐỀ
        // ==========================================
        async function loadWishesList() {
            const container = document.getElementById('quickWishesList');
            container.innerHTML = '<div class="text-xs text-rose-500 py-1">Đang tải lời chúc...</div>';
            try {
                const res = await fetch(`/api/wishes?category=${selectedCategory}`);
                const data = await res.json();
                container.innerHTML = '';
                data.wishes.forEach((w) => {
                    const pill = document.createElement('div');
                    pill.className = 'quick-wish-pill text-xs p-2 rounded-xl bg-white/80 border border-rose-100 cursor-pointer text-rose-900 truncate';
                    pill.textContent = w;
                    pill.title = 'Bấm để dùng lời chúc này';
                    pill.onclick = () => {
                        document.getElementById('messageInput').value = w;
                        triggerAutoSync();
                    };
                    container.appendChild(pill);
                });
            } catch (e) {
                container.innerHTML = '<div class="text-xs text-rose-400">Không thể tải danh sách lời chúc</div>';
            }
        }

        // Đổi ngẫu nhiên lời chúc
        async function fetchRandomWish() {
            try {
                const res = await fetch(`/api/random-wish?category=${selectedCategory}`);
                const data = await res.json();
                document.getElementById('messageInput').value = data.wish;
                triggerAutoSync();
            } catch (e) {}
        }

        // ==========================================
        // TỰ ĐỘNG ĐỒNG BỘ NỘI DUNG VỚI QR VÀ DATABASE
        // ==========================================
        function triggerAutoSync() {
            const badge = document.getElementById('syncBadge');
            badge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-100 text-amber-800 text-xs font-bold border border-amber-300 shadow-sm transition-all';
            badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-amber-500 animate-ping"></span><span>Đang lưu...</span>';

            clearTimeout(syncTimeout);
            syncTimeout = setTimeout(() => {
                syncGift(false);
            }, 350);
        }

        async function syncGift(isManualClick) {
            const receiver = document.getElementById('receiverInput').value.trim() || 'Người Phụ Nữ Tuyệt Vời';
            const sender = document.getElementById('senderInput').value.trim() || 'Một người luôn yêu thương bạn';
            const message = document.getElementById('messageInput').value.trim() || 'Chúc mừng ngày Phụ nữ Việt Nam 20/10!';
            const baseUrl = document.getElementById('baseUrlInput').value.trim().replace(/\/$/, '');

            try {
                const res = await fetch('/api/create-gift', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        id: currentGiftId, // Nếu đã có id thì cập nhật đè lên id đó
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

                // Cập nhật Poster bên phải
                document.getElementById('posterReceiver').textContent = receiver;
                document.getElementById('posterSender').textContent = `Từ: ${sender}`;
                document.getElementById('shortUrlOutput').value = currentGiftUrl;
                document.getElementById('openGiftPageBtn').href = currentGiftUrl;

                // Vẽ lại mã QR Code với link mới
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

                // Cập nhật trạng thái badge
                const badge = document.getElementById('syncBadge');
                badge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold border border-emerald-300 shadow-sm transition-all';
                badge.innerHTML = '<span class="w-2 h-2 rounded-full bg-emerald-500"></span><span>Đã đồng bộ QR</span>';

                if (isManualClick) {
                    refreshStats();
                }
            } catch (err) {
                const badge = document.getElementById('syncBadge');
                badge.className = 'inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-rose-100 text-rose-800 text-xs font-bold border border-rose-300';
                badge.innerHTML = '<span>Lỗi kết nối</span>';
            }
        }

        function createNewGiftFresh() {
            currentGiftId = null;
            syncGift(true);
        }

        async function refreshStats() {
            if (!currentGiftId) return;
            try {
                const res = await fetch(`/api/stats/${currentGiftId}`);
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('statViews').textContent = data.views;
                    document.getElementById('statHearts').textContent = data.hearts;
                }
            } catch (e) {}
        }

        function copyGiftUrl() {
            const input = document.getElementById('shortUrlOutput');
            input.select();
            navigator.clipboard.writeText(input.value);
            alert('Đã sao chép link trang nhận quà!');
        }

        // Tải ảnh Poster QR PNG cao cấp
        function downloadPosterPNG() {
            const qrImg = document.querySelector('#qrcodeContainer img') || document.querySelector('#qrcodeContainer canvas');
            if (!qrImg) return;

            const canvas = document.createElement('canvas');
            canvas.width = 800;
            canvas.height = 1080;
            const ctx = canvas.getContext('2d');

            // Nền Gradient
            const grad = ctx.createLinearGradient(0, 0, 800, 1080);
            grad.addColorStop(0, '#fff5f7');
            grad.addColorStop(0.5, '#fce7f3');
            grad.addColorStop(1, '#fed7aa');
            ctx.fillStyle = grad;
            ctx.fillRect(0, 0, 800, 1080);

            // Viền vàng hồng
            ctx.strokeStyle = '#f43f5e';
            ctx.lineWidth = 6;
            ctx.strokeRect(30, 30, 740, 1020);

            ctx.fillStyle = '#be123c';
            ctx.font = 'bold 24px sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('HAPPY VIETNAMESE WOMEN\'S DAY 20/10', 400, 110);

            ctx.fillStyle = '#881337';
            ctx.font = 'italic bold 46px serif';
            ctx.fillText(document.getElementById('posterReceiver').textContent, 400, 185);

            // Khung chứa QR
            ctx.fillStyle = '#ffffff';
            ctx.beginPath();
            ctx.roundRect(185, 230, 430, 430, 28);
            ctx.fill();

            ctx.drawImage(qrImg, 220, 265, 360, 360);

            ctx.fillStyle = '#9f1239';
            ctx.font = 'bold 28px sans-serif';
            ctx.fillText('📱 Quét mã QR để mở Hộp Quà 3D', 400, 725);

            ctx.fillStyle = '#be123c';
            ctx.font = 'italic 24px sans-serif';
            ctx.fillText(document.getElementById('posterSender').textContent, 400, 785);

            ctx.fillStyle = '#e11d48';
            ctx.font = '20px monospace';
            ctx.fillText(currentGiftUrl, 400, 930);

            const link = document.createElement('a');
            link.download = `Thiep-20-10-${currentGiftId || 'QR'}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        }

        // ==========================================
        // GẮN SỰ KIỆN LẮNG NGHE THAY ĐỔI
        // ==========================================
        document.querySelectorAll('.cat-chip').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.cat-chip').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                selectedCategory = btn.dataset.cat;
                loadWishesList();
                fetchRandomWish();
            });
        });

        document.querySelectorAll('.flower-card').forEach(card => {
            card.addEventListener('click', () => {
                document.querySelectorAll('.flower-card').forEach(c => c.classList.remove('active'));
                card.classList.add('active');
                selectedFlower = card.dataset.flower;
                updateFlowerPreview();
                triggerAutoSync();
            });
        });

        // Tự động sync khi người dùng gõ nội dung bất kỳ
        document.getElementById('receiverInput').addEventListener('input', triggerAutoSync);
        document.getElementById('senderInput').addEventListener('input', triggerAutoSync);
        document.getElementById('messageInput').addEventListener('input', triggerAutoSync);
        document.getElementById('baseUrlInput').addEventListener('input', triggerAutoSync);

        window.addEventListener('DOMContentLoaded', () => {
            const baseInput = document.getElementById('baseUrlInput');
            if (baseInput && (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1')) {
                baseInput.value = window.location.origin;
            }
            updateFlowerPreview();
            loadWishesList();
            syncGift(true);
        });
    </script>
</body>
</html>
"""

# ==========================================
# TRANG 2: TRANG MỞ HỘP QUÀ & HOA 3D CHO NGƯỜI NHẬN
# ==========================================
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
            background: radial-gradient(circle at 50% 20%, #4c0519 0%, #1f020c 60%, #0d0106 100%);
            min-height: 100vh;
            overflow-x: hidden;
            color: #fff;
        }
        .font-script { font-family: 'Dancing Script', cursive; }
        .font-serif-title { font-family: 'Playfair Display', serif; }

        /* HỘP QUÀ 3D TƯƠNG TÁC */
        .gift-stage { perspective: 1200px; }
        .gift-box-wrapper {
            cursor: pointer;
            transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            animation: floatBox 3.5s ease-in-out infinite;
        }
        .gift-box-wrapper:hover {
            transform: scale(1.08);
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
            transform: translateY(-160px) rotate(24deg) scale(0.85);
            opacity: 0;
            transition: all 0.85s cubic-bezier(0.22, 1, 0.36, 1);
        }

        /* BÓ HOA BÙNG NỞ VÀ ĐUNG ĐƯA */
        .bouquet-appear {
            animation: bloomUp 1.1s cubic-bezier(0.16, 1, 0.3, 1) forwards, gentleSway 4.8s ease-in-out 1.1s infinite;
        }
        @keyframes bloomUp {
            0% { opacity: 0; transform: translateY(90px) scale(0.35); }
            70% { opacity: 1; transform: translateY(-10px) scale(1.05); }
            100% { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes gentleSway {
            0%, 100% { transform: rotate(-1.5deg) translateY(0px); }
            50% { transform: rotate(1.5deg) translateY(-8px); }
        }

        /* BỨC THƯ TAY PHONG BÌ SÁP ONG */
        .parchment-card {
            background: linear-gradient(165deg, #fffdfa 0%, #fff1f5 55%, #ffe4ec 100%);
            box-shadow: 0 25px 70px rgba(244, 63, 94, 0.35), 0 0 0 1px rgba(251, 113, 133, 0.4);
            color: #4c0519;
        }
        .glow-aura {
            background: radial-gradient(circle, rgba(244,63,94,0.48) 0%, rgba(251,191,36,0.18) 45%, transparent 70%);
            filter: blur(28px);
        }
    </style>
</head>
<body class="relative flex flex-col items-center justify-center min-h-screen px-4 py-8">

    <!-- Canvas Cánh Hoa & Pháo Hoa Trái Tim -->
    <canvas id="petalCanvas" class="fixed inset-0 pointer-events-none z-10"></canvas>

    <!-- Nút Bật/Tắt Nhạc Góc Phải -->
    <button id="musicBtn" onclick="toggleMusic()"
        class="fixed top-5 right-5 z-50 px-4 py-2 rounded-full bg-white/15 backdrop-blur-md border border-white/25 text-xs font-semibold text-pink-100 flex items-center gap-2 hover:bg-white/25 transition shadow-lg">
        <span id="musicIcon">🎵</span> <span id="musicLabel">Nhạc 20/10</span>
    </button>

    <!-- ==================================================== -->
    <!-- MÀN HÌNH 1: HỘP QUÀ 3D CHỜ NGƯỜI NHẬN CHẠM MỞ -->
    <!-- ==================================================== -->
    <div id="stageClosed" class="relative z-20 text-center max-w-md mx-auto flex flex-col items-center">
        <div class="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-rose-500/20 border border-rose-400/30 text-rose-200 text-xs font-semibold tracking-wider uppercase mb-4 shadow-sm">
            ✨ Happy Vietnamese Women's Day 20/10 ✨
        </div>

        <h1 class="font-serif-title text-2xl sm:text-4xl font-bold text-white mb-2">
            Món Quà Dành Riêng Cho
        </h1>
        <div class="font-script text-4xl sm:text-5xl text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-pink-300 to-rose-300 py-1 mb-6">
            {{ gift.receiver }}
        </div>

        <!-- Hộp Quà 3D Tương Tác -->
        <div class="relative gift-stage my-2 flex items-center justify-center">
            <div class="glow-aura absolute w-72 h-72 rounded-full"></div>

            <div id="giftBox" onclick="openGiftSequence()" class="gift-box-wrapper relative w-64 h-64 flex flex-col items-center justify-center">
                <!-- Nắp Hộp Quà + Nơ Lụa Vàng -->
                <div id="giftLid" class="relative z-20 -mb-3 transition-transform duration-700">
                    <svg width="220" height="95" viewBox="0 0 220 95" fill="none">
                        <path d="M110 42C85 5 45 12 55 40C62 56 95 48 110 42Z" fill="url(#gGoldGrad)" stroke="#fde68a" stroke-width="2"/>
                        <path d="M110 42C135 5 175 12 165 40C158 56 125 48 110 42Z" fill="url(#gGoldGrad)" stroke="#fde68a" stroke-width="2"/>
                        <circle cx="110" cy="42" r="11" fill="#fbbf24" stroke="#fef08a" stroke-width="3"/>
                        <rect x="15" y="46" width="190" height="42" rx="10" fill="url(#gLidGrad)" stroke="#fda4af" stroke-width="2"/>
                        <rect x="96" y="46" width="28" height="42" fill="url(#gGoldGrad)"/>
                    </svg>
                </div>

                <!-- Thân Hộp Quà -->
                <div class="relative z-10">
                    <svg width="200" height="145" viewBox="0 0 200 145" fill="none">
                        <rect x="12" y="4" width="176" height="135" rx="14" fill="url(#gBoxGrad)" stroke="#fb7185" stroke-width="2"/>
                        <rect x="86" y="4" width="28" height="135" fill="url(#gGoldGrad)"/>
                        <rect x="12" y="58" width="176" height="24" fill="url(#gGoldGrad)" fill-opacity="0.9"/>
                        <path d="M100 84C100 84 82 72 82 61C82 54 88 50 94 50C98 50 100 53 100 53C100 53 102 50 106 50C112 50 118 54 118 61C118 72 100 84 100 84Z" fill="#fff1f2"/>
                        <defs>
                            <linearGradient id="gBoxGrad" x1="12" y1="4" x2="188" y2="139" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#e11d48"/>
                                <stop offset="1" stop-color="#881337"/>
                            </linearGradient>
                            <linearGradient id="gLidGrad" x1="15" y1="46" x2="205" y2="88" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#f43f5e"/>
                                <stop offset="1" stop-color="#be123c"/>
                            </linearGradient>
                            <linearGradient id="gGoldGrad" x1="0" y1="0" x2="200" y2="140" gradientUnits="userSpaceOnUse">
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
        <p class="mt-1 text-xs text-pink-300/70">
            Được gửi từ: <span class="text-pink-100 font-semibold">{{ gift.sender }}</span>
        </p>
    </div>

    <!-- ============================================================ -->
    <!-- MÀN HÌNH 2: BÓ HOA 3D BÙNG NỞ & BỨC THƯ TAY HOÀNG GIA -->
    <!-- ============================================================ -->
    <div id="stageOpened" class="hidden relative z-20 w-full max-w-5xl mx-auto">
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">

            <!-- CỘT TRÁI: BÓ HOA NGHỆ THUẬT LỚN ĐUNG ĐƯA -->
            <div class="lg:col-span-5 flex flex-col items-center justify-center">
                <div class="relative flex items-center justify-center">
                    <div class="glow-aura absolute w-80 h-80 rounded-full"></div>
                    <div id="bouquetContainer" class="bouquet-appear relative z-10 w-72 sm:w-84"></div>
                </div>
                <div class="mt-3 px-5 py-1.5 rounded-full bg-white/10 backdrop-blur-md border border-white/20 text-xs text-amber-200 font-medium shadow-md">
                    💐 Bó hoa tươi thắm dành tặng riêng {{ gift.receiver }}
                </div>
            </div>

            <!-- CỘT PHẢI: BỨC THƯ TAY THIỆP SÁP ONG -->
            <div class="lg:col-span-7">
                <div class="parchment-card rounded-3xl p-6 sm:p-10 relative overflow-hidden">
                    <!-- Góc trang trí sáp ong cổ điển -->
                    <div class="flex items-center justify-between border-b border-rose-200 pb-4 mb-5">
                        <div>
                            <span class="text-[11px] font-bold uppercase tracking-widest text-rose-500 block">Thư Chúc Mừng 20/10</span>
                            <h2 class="font-script text-3xl sm:text-4xl text-rose-800 mt-0.5">Gửi {{ gift.receiver }}</h2>
                        </div>
                        <div class="w-12 h-12 rounded-full bg-gradient-to-br from-rose-600 to-pink-700 text-amber-200 flex items-center justify-center shadow-lg border-2 border-amber-200 font-serif-title font-bold text-sm">
                            20/10
                        </div>
                    </div>

                    <!-- Nội dung lời chúc chạy chữ typewriter -->
                    <div class="min-h-[140px] flex items-center">
                        <p id="typewriterText" class="text-base sm:text-lg leading-relaxed text-rose-950 font-medium whitespace-pre-line"></p>
                    </div>

                    <!-- Chữ ký người gửi & Nút thả tim cảm ơn -->
                    <div class="mt-6 pt-4 border-t border-rose-200/80 flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <span class="text-xs text-rose-500 block">Người gửi yêu thương,</span>
                            <span class="font-script text-2xl sm:text-3xl text-rose-800">{{ gift.sender }}</span>
                        </div>

                        <!-- Nút Thả Tim -->
                        <button id="heartBtn" onclick="sendThankYouHeart()"
                            class="px-5 py-3 rounded-full bg-gradient-to-r from-rose-600 via-pink-600 to-rose-500 text-white text-xs sm:text-sm font-bold shadow-lg shadow-rose-500/35 hover:scale-105 active:scale-95 transition flex items-center gap-2">
                            <span>❤️ Thả Tim Cảm Ơn</span>
                            <span id="heartCountBadge" class="px-2.5 py-0.5 rounded-full bg-white/20 text-xs">{{ gift.hearts }}</span>
                        </button>
                    </div>

                    <div class="mt-4 text-center">
                        <a href="/" class="text-[11px] text-rose-500 hover:text-rose-700 underline font-semibold">
                            ✨ Tạo một thiệp & hộp quà tương tự cho người thân yêu
                        </a>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- SCRIPT VẼ HOA VÀ LOGIC MỞ HỘP TRÊN TRANG NHẬN QUÀ -->
    <script>
        const GIFT_ID = {{ gift.id | tojson }};
        const FULL_MESSAGE = {{ gift.message | tojson }};
        const FLOWER_TYPE = {{ gift.flower_type | tojson }};

        // Render đúng loại hoa của món quà (Tulip, Rose, Sunflower, Peony)
        function getGiftBouquetSVG(type) {
            if (type === 'tulip') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-2xl">
                    <defs>
                        <linearGradient id="gtWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fce7f3"/></linearGradient>
                        <linearGradient id="gtWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f472b6"/><stop offset="100%" stop-color="#db2777"/></linearGradient>
                        <linearGradient id="gtPetal1" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#f43f5e"/><stop offset="70%" stop-color="#ec4899"/><stop offset="100%" stop-color="#ffe4e6"/></linearGradient>
                        <linearGradient id="gtPetal2" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#fb7185"/><stop offset="60%" stop-color="#f472b6"/><stop offset="100%" stop-color="#fff1f2"/></linearGradient>
                        <linearGradient id="gtLeaf" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stop-color="#4ade80"/><stop offset="100%" stop-color="#15803d"/></linearGradient>
                    </defs>
                    <path d="M70 190 L190 435 L310 190 Q250 140 190 160 Q130 140 70 190 Z" fill="url(#gtWrap1)" stroke="#f472b6" stroke-width="2"/>
                    <path d="M100 170 L190 415 L280 170 Z" fill="#ffffff" fill-opacity="0.85"/>
                    <path d="M190 290 Q120 200 100 95 Q145 155 185 245 Z" fill="url(#gtLeaf)" opacity="0.95"/>
                    <path d="M190 290 Q260 200 280 95 Q235 155 195 245 Z" fill="url(#gtLeaf)" opacity="0.95"/>
                    <path d="M190 290 Q70 230 65 140 Q110 190 180 260 Z" fill="#22c55e" opacity="0.9"/>
                    <path d="M190 290 Q310 230 315 140 Q270 190 200 260 Z" fill="#22c55e" opacity="0.9"/>
                    <path d="M190 310 L190 120" stroke="#15803d" stroke-width="6" stroke-linecap="round"/>
                    <path d="M190 310 L135 155" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L245 155" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L95 195" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 310 L285 195" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <!-- 5 Búp hoa Tulip -->
                    <g transform="translate(190, 110)">
                        <path d="M -16 10 C -22 -20 -15 -55 0 -65 C 15 -55 22 -20 16 10 Z" fill="url(#gtPetal1)"/>
                        <path d="M -24 15 C -30 -15 -18 -45 -6 -52 C -12 -15 0 10 -24 15 Z" fill="url(#gtPetal2)"/>
                        <path d="M 24 15 C 30 -15 18 -45 6 -52 C 12 -15 0 10 24 15 Z" fill="url(#gtPetal2)"/>
                    </g>
                    <g transform="translate(135, 145) rotate(-14)">
                        <path d="M -15 10 C -20 -18 -14 -50 0 -60 C 14 -50 20 -18 15 10 Z" fill="url(#gtPetal1)"/>
                        <path d="M -22 14 C -28 -12 -16 -40 -5 -48 C -10 -12 0 10 -22 14 Z" fill="url(#gtPetal2)"/>
                        <path d="M 22 14 C 28 -12 16 -40 5 -48 C 10 -12 0 10 22 14 Z" fill="url(#gtPetal2)"/>
                    </g>
                    <g transform="translate(245, 145) rotate(14)">
                        <path d="M -15 10 C -20 -18 -14 -50 0 -60 C 14 -50 20 -18 15 10 Z" fill="url(#gtPetal1)"/>
                        <path d="M -22 14 C -28 -12 -16 -40 -5 -48 C -10 -12 0 10 -22 14 Z" fill="url(#gtPetal2)"/>
                        <path d="M 22 14 C 28 -12 16 -40 5 -48 C 10 -12 0 10 22 14 Z" fill="url(#gtPetal2)"/>
                    </g>
                    <g transform="translate(95, 190) rotate(-22)">
                        <path d="M -14 8 C -18 -15 -12 -42 0 -52 C 12 -42 18 -15 14 8 Z" fill="url(#gtPetal1)"/>
                        <path d="M -20 12 C -25 -10 -14 -35 -4 -42 C -9 -10 0 8 -20 12 Z" fill="url(#gtPetal2)"/>
                        <path d="M 20 12 C 25 -10 14 -35 4 -42 C 9 -10 0 8 20 12 Z" fill="url(#gtPetal2)"/>
                    </g>
                    <g transform="translate(285, 190) rotate(22)">
                        <path d="M -14 8 C -18 -15 -12 -42 0 -52 C 12 -42 18 -15 14 8 Z" fill="url(#gtPetal1)"/>
                        <path d="M -20 12 C -25 -10 -14 -35 -4 -42 C -9 -10 0 8 -20 12 Z" fill="url(#gtPetal2)"/>
                        <path d="M 20 12 C 25 -10 14 -35 4 -42 C 9 -10 0 8 20 12 Z" fill="url(#gtPetal2)"/>
                    </g>
                    <path d="M85 220 L190 435 L295 220 Q240 260 190 240 Q140 260 85 220 Z" fill="url(#gtWrap2)" opacity="0.95"/>
                    <path d="M120 235 L190 435 L260 235 Q190 270 120 235 Z" fill="#be185d" opacity="0.9"/>
                    <path d="M190 335 C150 305 120 325 140 350 C155 362 180 345 190 335 Z" fill="#f472b6" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M190 335 C230 305 260 325 240 350 C225 362 200 345 190 335 Z" fill="#f472b6" stroke="#fbcfe8" stroke-width="2"/>
                    <circle cx="190" cy="335" r="10" fill="#fff1f2" stroke="#f472b6" stroke-width="3"/>
                </svg>`;
            } else if (type === 'sunflower') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-2xl">
                    <defs>
                        <linearGradient id="gsWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fef9c3"/><stop offset="100%" stop-color="#fef08a"/></linearGradient>
                        <linearGradient id="gsWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#b45309"/><stop offset="100%" stop-color="#78350f"/></linearGradient>
                        <radialGradient id="gsCenter" cx="50%" cy="50%" r="50%"><stop offset="0%" stop-color="#2a1202"/><stop offset="65%" stop-color="#451a03"/><stop offset="100%" stop-color="#a16207"/></radialGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#gsWrap1)" stroke="#d97706" stroke-width="2"/>
                    <g stroke="#15803d" stroke-width="5" stroke-linecap="round">
                        <path d="M190 280 L190 115"/><path d="M190 280 L125 180"/><path d="M190 280 L255 180"/>
                    </g>
                    <path d="M140 230 Q90 180 80 130 Q120 160 150 210 Z" fill="#15803d"/>
                    <path d="M240 230 Q290 180 300 130 Q260 160 230 210 Z" fill="#15803d"/>
                    ${renderGiftSunflower(190, 110, 52)}
                    ${renderGiftSunflower(125, 180, 44)}
                    ${renderGiftSunflower(255, 180, 44)}
                    <g fill="#ffffff" stroke="#fef08a" stroke-width="1.5">
                        <circle cx="85" cy="140" r="7"/><circle cx="85" cy="140" r="3" fill="#eab308"/>
                        <circle cx="295" cy="140" r="7"/><circle cx="295" cy="140" r="3" fill="#eab308"/>
                    </g>
                    <path d="M80 210 L190 435 L300 210 Q240 255 190 235 Q140 255 80 210 Z" fill="url(#gsWrap2)" opacity="0.95"/>
                    <path d="M110 225 L190 435 L270 225 Q190 270 110 225 Z" fill="#451a03" opacity="0.9"/>
                    <path d="M190 330 C150 295 115 315 135 345 C150 360 175 340 190 330 Z" fill="#f59e0b" stroke="#fef08a" stroke-width="2"/>
                    <path d="M190 330 C230 295 265 315 245 345 C230 360 205 340 190 330 Z" fill="#f59e0b" stroke="#fef08a" stroke-width="2"/>
                    <circle cx="190" cy="330" r="10" fill="#fef08a" stroke="#d97706" stroke-width="3"/>
                </svg>`;
            } else if (type === 'peony') {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-2xl">
                    <defs>
                        <linearGradient id="gpWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fce7f3"/></linearGradient>
                        <linearGradient id="gpWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#f472b6"/><stop offset="100%" stop-color="#9d174d"/></linearGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#gpWrap1)" stroke="#f472b6" stroke-width="2"/>
                    <g fill="#64748b" opacity="0.75">
                        <ellipse cx="95" cy="115" rx="15" ry="10" transform="rotate(-30 95 115)"/>
                        <ellipse cx="285" cy="115" rx="15" ry="10" transform="rotate(30 285 115)"/>
                        <ellipse cx="190" cy="50" rx="16" ry="11"/>
                    </g>
                    <path d="M190 280 L190 120" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L130 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L250 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    ${renderGiftPeony(190, 115, 50)}
                    ${renderGiftPeony(125, 175, 42)}
                    ${renderGiftPeony(255, 175, 42)}
                    ${renderGiftPeony(190, 205, 44)}
                    <path d="M80 215 L190 435 L300 215 Q240 260 190 240 Q140 260 80 215 Z" fill="url(#gpWrap2)" opacity="0.95"/>
                    <path d="M115 230 L190 435 L265 230 Q190 275 115 230 Z" fill="#831843" opacity="0.9"/>
                    <path d="M190 335 C150 300 115 320 135 350 C150 365 175 345 190 335 Z" fill="#db2777" stroke="#fbcfe8" stroke-width="2"/>
                    <path d="M190 335 C230 300 265 320 245 350 C230 365 205 345 190 335 Z" fill="#db2777" stroke="#fbcfe8" stroke-width="2"/>
                    <circle cx="190" cy="335" r="10" fill="#fff1f2" stroke="#db2777" stroke-width="3"/>
                </svg>`;
            } else {
                return `
                <svg viewBox="0 0 380 460" class="w-full h-auto drop-shadow-2xl">
                    <defs>
                        <linearGradient id="grWrap1" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fff1f2"/><stop offset="100%" stop-color="#fecdd3"/></linearGradient>
                        <linearGradient id="grWrap2" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#be123c"/><stop offset="100%" stop-color="#881337"/></linearGradient>
                        <linearGradient id="grGold" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#fef08a"/><stop offset="50%" stop-color="#f59e0b"/><stop offset="100%" stop-color="#d97706"/></linearGradient>
                    </defs>
                    <path d="M60 180 L190 435 L320 180 Q255 130 190 150 Q125 130 60 180 Z" fill="url(#grWrap1)" stroke="#fda4af" stroke-width="2"/>
                    <g fill="#166534">
                        <path d="M120 140 Q80 120 70 90 Q105 105 125 130 Z"/>
                        <path d="M260 140 Q300 120 310 90 Q275 105 255 130 Z"/>
                    </g>
                    <path d="M190 280 L190 120" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L125 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    <path d="M190 280 L255 170" stroke="#15803d" stroke-width="5" stroke-linecap="round"/>
                    ${renderGiftRose(190, 110, 48)}
                    ${renderGiftRose(120, 160, 42)}
                    ${renderGiftRose(260, 160, 42)}
                    ${renderGiftRose(150, 205, 40)}
                    ${renderGiftRose(230, 205, 40)}
                    <g fill="#ffffff" opacity="0.95">
                        <circle cx="85" cy="115" r="5"/><circle cx="98" cy="105" r="4"/><circle cx="295" cy="115" r="5"/><circle cx="282" cy="105" r="4"/><circle cx="190" cy="48" r="5"/>
                    </g>
                    <path d="M80 215 L190 435 L300 215 Q240 260 190 240 Q140 260 80 215 Z" fill="url(#grWrap2)" opacity="0.95"/>
                    <path d="M115 230 L190 435 L265 230 Q190 275 115 230 Z" fill="#4c0519" opacity="0.9"/>
                    <path d="M190 335 C150 300 115 320 135 350 C150 365 175 345 190 335 Z" fill="url(#grGold)" stroke="#fef08a" stroke-width="2"/>
                    <path d="M190 335 C230 300 265 320 245 350 C230 365 205 345 190 335 Z" fill="url(#grGold)" stroke="#fef08a" stroke-width="2"/>
                    <circle cx="190" cy="335" r="10" fill="#fef08a" stroke="#d97706" stroke-width="3"/>
                </svg>`;
            }
        }

        function renderGiftRose(cx, cy, r) {
            return `
            <g transform="translate(${cx}, ${cy})">
                <circle cx="0" cy="0" r="${r}" fill="#881337"/>
                <path d="M ${-r} 0 C ${-r*1.1} ${-r*0.8} ${-r*0.2} ${-r*1.1} 0 ${-r*0.9} C ${r*0.6} ${-r*1.1} ${r} ${-r*0.6} ${r} 0 C ${r*1.1} ${r*0.7} 0 ${r*1.1} ${-r} 0 Z" fill="#9f1239"/>
                <path d="M ${-r*0.75} ${-r*0.5} C ${-r*0.9} ${r*0.3} ${-r*0.2} ${r*0.9} ${r*0.5} ${r*0.7} C ${r*0.9} ${r*0.1} ${r*0.7} ${-r*0.7} ${-r*0.75} ${-r*0.5} Z" fill="#be123c"/>
                <path d="M ${-r*0.5} ${r*0.4} C ${-r*0.7} ${-r*0.5} ${r*0.2} ${-r*0.8} ${r*0.6} ${-r*0.3} C ${r*0.8} ${r*0.5} ${-r*0.1} ${r*0.8} ${-r*0.5} ${r*0.4} Z" fill="#e11d48"/>
                <ellipse cx="0" cy="0" rx="${r*0.2}" ry="${r*0.14}" fill="#fb7185"/>
            </g>`;
        }

        function renderGiftSunflower(cx, cy, r) {
            let petals = '';
            for (let i = 0; i < 18; i++) {
                const deg = i * 20;
                petals += `<path d="M 0 0 C -7 -${r*0.4} -5 -${r*0.9} 0 -${r} C 5 -${r*0.9} 7 -${r*0.4} 0 0 Z" transform="rotate(${deg})" fill="${i % 2 === 0 ? '#f59e0b' : '#facc15'}"/>`;
            }
            return `
            <g transform="translate(${cx}, ${cy})">
                ${petals}
                <circle cx="0" cy="0" r="${r*0.48}" fill="url(#gsCenter)"/>
                <circle cx="0" cy="0" r="${r*0.38}" fill="#2a1202" opacity="0.9"/>
                <circle cx="0" cy="0" r="${r*0.18}" fill="#78350f"/>
            </g>`;
        }

        function renderGiftPeony(cx, cy, r) {
            return `
            <g transform="translate(${cx}, ${cy})">
                <circle cx="0" cy="0" r="${r}" fill="#9d174d"/>
                <path d="M ${-r} 0 C ${-r} ${-r*0.8} ${-r*0.3} ${-r*1.05} 0 ${-r*0.95} C ${r*0.4} ${-r*1.05} ${r} ${-r*0.7} ${r} 0 C ${r*1.05} ${r*0.8} 0 ${r*1.05} ${-r} 0 Z" fill="#be185d"/>
                <path d="M ${-r*0.85} ${-r*0.3} C ${-r*0.8} ${r*0.7} ${r*0.3} ${r*0.85} ${r*0.7} ${r*0.4} C ${r*0.85} ${-r*0.5} ${-r*0.3} ${-r*0.8} ${-r*0.85} ${-r*0.3} Z" fill="#db2777"/>
                <path d="M ${-r*0.65} ${r*0.2} C ${-r*0.7} ${-r*0.5} ${r*0.1} ${-r*0.7} ${r*0.55} ${-r*0.2} C ${r*0.65} ${r*0.5} ${-r*0.2} ${r*0.7} ${-r*0.65} ${r*0.2} Z" fill="#ec4899"/>
                <circle cx="0" cy="0" r="${r*0.26}" fill="#fbcfe8"/>
                <circle cx="1" cy="1" r="${r*0.1}" fill="#fbbf24"/>
            </g>`;
        }

        // ==========================================
        // MỞ HỘP QUÀ -> BÙNG HOA -> GÕ CHỮ
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

                document.getElementById('bouquetContainer').innerHTML = getGiftBouquetSVG(FLOWER_TYPE);
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
            }, 26);
        }

        // ==========================================
        // THẢ TIM CẢM ƠN
        // ==========================================
        async function sendThankYouHeart() {
            burstHeartsAndPetals();
            try {
                const res = await fetch(`/api/heart/${GIFT_ID}`, { method: 'POST' });
                if (res.ok) {
                    const data = await res.json();
                    document.getElementById('heartCountBadge').textContent = data.hearts;
                }
            } catch (e) {}
        }

        // ==========================================
        // NHẠC MUSIC BOX DỊU DÀNG
        // ==========================================
        let audioCtx = null;
        let isPlayingMusic = false;
        let melodyTimer = null;

        function playRomanticMelody() {
            if (isPlayingMusic) return;
            try {
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
                    gain.gain.exponentialRampToValueAtTime(0.12, audioCtx.currentTime + 0.04);
                    gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 1.15);

                    osc.connect(gain);
                    gain.connect(audioCtx.destination);
                    osc.start();
                    osc.stop(audioCtx.currentTime + 1.2);
                    idx++;
                }, 440);
            } catch (e) {}
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
        // MƯA CÁNH HOA & PHÁO TIM CANVAS
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

        for (let i = 0; i < 40; i++) {
            particles.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: 5 + Math.random() * 7,
                vx: -0.5 + Math.random() * 1,
                vy: 0.8 + Math.random() * 1.4,
                angle: Math.random() * Math.PI * 2,
                spin: -0.02 + Math.random() * 0.04,
                color: ['#fda4af', '#fb7185', '#f43f5e', '#fecdd3', '#fef08a'][Math.floor(Math.random() * 5)],
                burst: false
            });
        }

        function burstHeartsAndPetals() {
            for (let i = 0; i < 50; i++) {
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
                    color: ['#fbbf24', '#f43f5e', '#ec4899', '#ffe4e6', '#fb7185'][Math.floor(Math.random() * 5)],
                    burst: true,
                    life: 95
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
# CÁC ROUTE CỦA FLASK
# ==========================================
@app.route("/")
def index():
    default_base_url = get_base_url()
    return render_template("create.html", default_base_url=default_base_url)

@app.route("/qua/<gift_id>")
def view_gift(gift_id):
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

@app.route("/api/wishes")
def api_wishes():
    cat = request.args.get("category", "all")
    if cat in WISHES_DB:
        return jsonify({"category": cat, "wishes": WISHES_DB[cat]})
    all_w = []
    for c, wishes in WISHES_DB.items():
        all_w.extend(wishes)
    return jsonify({"category": "all", "wishes": all_w})

@app.route("/api/random-wish")
def api_random_wish():
    cat = request.args.get("category", "all")
    if cat in WISHES_DB:
        pool = WISHES_DB[cat]
    else:
        pool = [w for group in WISHES_DB.values() for w in group]
    return jsonify({"wish": secrets.choice(pool)})

@app.route("/api/create-gift", methods=["POST"])
def api_create_gift():
    """Lưu hoặc cập nhật quà tặng vào SQLite; QR và link đồng bộ tức thì"""
    data = request.get_json(force=True)
    gift_id = data.get("id")
    if not gift_id or len(gift_id) > 12:
        gift_id = secrets.token_urlsafe(4).replace("-", "").replace("_", "")[:6].lower()
    else:
        gift_id = gift_id.strip().lower()

    sender = (data.get("sender") or "Một người luôn yêu thương bạn").strip()
    receiver = (data.get("receiver") or "Người Phụ Nữ Tuyệt Vời").strip()
    category = (data.get("category") or "all").strip()
    message = (data.get("message") or "Chúc mừng ngày Phụ nữ Việt Nam 20/10!").strip()
    flower_type = (data.get("flower_type") or "rose").strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM gifts WHERE id = ?", (gift_id,))
    if c.fetchone():
        c.execute("""
            UPDATE gifts SET sender = ?, receiver = ?, category = ?, message = ?, flower_type = ?
            WHERE id = ?
        """, (sender, receiver, category, message, flower_type, gift_id))
    else:
        c.execute("""
            INSERT INTO gifts (id, sender, receiver, category, message, flower_type, theme_color, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (gift_id, sender, receiver, category, message, flower_type, "rose", datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"id": gift_id, "url": f"/qua/{gift_id}"})

@app.route("/api/heart/<gift_id>", methods=["POST"])
def api_heart_gift(gift_id):
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
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT views, hearts FROM gifts WHERE id = ?", (gift_id,))
    row = c.fetchone()
    conn.close()
    if not row:
        return jsonify({"views": 0, "hearts": 0}), 404
    return jsonify({"views": row[0], "hearts": row[1]})

# Đảm bảo database và templates luôn được cập nhật khi chạy trực tiếp hoặc Gunicorn trên Render
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
