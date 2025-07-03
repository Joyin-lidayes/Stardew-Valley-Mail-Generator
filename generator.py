import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QSpinBox, QFileDialog, QGroupBox, QSplitter
)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageDraw, ImageFont

FONT_PATH = os.path.join('src', 'font', 'KNMaiyuan-Regular.ttf')
MAIL_IMG_DIR = os.path.join('src', 'mail_img')
GIFT_IMG_DIR = os.path.join('src', 'gift_img')

def get_img_list(folder):
    return [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

class PreviewLabel(QLabel):
    def __init__(self, parent=None, update_callback=None):
        super().__init__(parent)
        self.update_callback = update_callback
    def resizeEvent(self, event):
        if self.update_callback:
            self.update_callback()
        super().resizeEvent(event)

class MailGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("星露谷信件生成器")
        self.init_ui()
        self.update_preview()

    def init_ui(self):
        # 输入区
        self.title_edit = QLineEdit()
        self.body_edit = QTextEdit()
        self.signature_edit = QLineEdit()
        self.gift_text_edit = QLineEdit()
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(10, 60)
        self.font_size_spin.setValue(36)
        self.letter_spacing_spin = QSpinBox()
        self.letter_spacing_spin.setRange(0, 20)
        self.letter_spacing_spin.setValue(2)

        self.mail_img_combo = QComboBox()
        mail_imgs = get_img_list(MAIL_IMG_DIR)
        self.mail_img_combo.addItems(mail_imgs)
        # 默认选中 regular_horizontal.png，如不存在则选第一个
        if "regular_horizontal.png" in mail_imgs:
            self.mail_img_combo.setCurrentText("regular_horizontal.png")
        elif mail_imgs:
            self.mail_img_combo.setCurrentIndex(0)

        self.gift_img_combo = QComboBox()
        self.gift_img_combo.addItems(['无'] + get_img_list(GIFT_IMG_DIR))

        # 先创建所有礼物说明相关控件和边距控件
        self.gift_text_fontsize_spin = QSpinBox()
        self.gift_text_fontsize_spin.setRange(8, 40)
        self.gift_text_fontsize_spin.setValue(30)
        self.gift_text_gap_spin = QSpinBox()
        self.gift_text_gap_spin.setRange(0, 100)
        self.gift_text_gap_spin.setValue(10)
        self.gift_text_pos_combo = QComboBox()
        self.gift_text_pos_combo.addItems(["图标前", "图标后"])
        self.margin_top_spin = QSpinBox()
        self.margin_top_spin.setRange(0, 100)
        self.margin_top_spin.setValue(64)
        self.margin_bottom_spin = QSpinBox()
        self.margin_bottom_spin.setRange(0, 100)
        self.margin_bottom_spin.setValue(81)
        self.margin_h_spin = QSpinBox()
        self.margin_h_spin.setRange(0, 100)
        self.margin_h_spin.setValue(64)

        # 新增礼物图标大小可调控件
        self.gift_img_size_spin = QSpinBox()
        self.gift_img_size_spin.setRange(24, 128)
        self.gift_img_size_spin.setValue(64)

        # 先创建保存按钮
        self.save_btn = QPushButton("保存为图片")
        self.save_btn.clicked.connect(self.save_image)

        # 预览区
        self.preview_label = PreviewLabel(update_callback=self.update_preview)
        self.preview_label.setAlignment(Qt.AlignCenter)
        # 不设置固定大小，让其自适应

        # --- 分组1：标题正文署名 ---
        group1 = QGroupBox("信件内容")
        group1_layout = QVBoxLayout()
        group1_layout.addWidget(QLabel("标题："))
        group1_layout.addWidget(self.title_edit)
        group1_layout.addWidget(QLabel("正文："))
        group1_layout.addWidget(self.body_edit)
        group1_layout.addWidget(QLabel("署名："))
        group1_layout.addWidget(self.signature_edit)
        group1.setLayout(group1_layout)

        # --- 分组2：礼物说明相关 ---
        group2 = QGroupBox("礼物说明")
        group2_layout = QVBoxLayout()
        group2_layout.addWidget(QLabel("礼物说明："))
        group2_layout.addWidget(self.gift_text_edit)
        group2_layout.addWidget(QLabel("礼物图标："))
        group2_layout.addWidget(self.gift_img_combo)
        group2_layout.addWidget(QLabel("说明字体大小："))
        group2_layout.addWidget(self.gift_text_fontsize_spin)
        group2_layout.addWidget(QLabel("说明与图标间距："))
        group2_layout.addWidget(self.gift_text_gap_spin)
        group2_layout.addWidget(QLabel("说明位置："))
        group2_layout.addWidget(self.gift_text_pos_combo)
        group2_layout.addWidget(QLabel("图标大小："))
        group2_layout.addWidget(self.gift_img_size_spin)
        group2.setLayout(group2_layout)

        # --- 分组3：其余设置 ---
        group3 = QGroupBox("信纸与样式")
        group3_layout = QVBoxLayout()
        group3_layout.addWidget(QLabel("信纸选择："))
        group3_layout.addWidget(self.mail_img_combo)
        group3_layout.addWidget(QLabel("字体大小："))
        group3_layout.addWidget(self.font_size_spin)
        group3_layout.addWidget(QLabel("字体间距："))
        group3_layout.addWidget(self.letter_spacing_spin)
        group3_layout.addWidget(QLabel("上边距："))
        group3_layout.addWidget(self.margin_top_spin)
        group3_layout.addWidget(QLabel("下边距："))
        group3_layout.addWidget(self.margin_bottom_spin)
        group3_layout.addWidget(QLabel("左右边距："))
        group3_layout.addWidget(self.margin_h_spin)
        group3_layout.addWidget(self.save_btn)
        group3.setLayout(group3_layout)

        # 左侧分组布局
        left_layout = QVBoxLayout()
        left_layout.addWidget(group1)
        left_layout.addWidget(group2)
        left_layout.addWidget(group3)
        left_layout.addStretch(1)
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        left_widget.setMinimumWidth(260)
        # left_widget.setMaximumWidth(360)  # 移除最大宽度限制

        # 主布局，使用QSplitter实现左右分区可拉伸
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(self.preview_label)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setCollapsible(0, False)
        # 移除 setSizes，允许自由拖动缩放
        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # 事件绑定
        self.title_edit.textChanged.connect(lambda: self.update_preview())
        self.body_edit.textChanged.connect(lambda: self.update_preview())
        self.signature_edit.textChanged.connect(lambda: self.update_preview())
        self.gift_text_edit.textChanged.connect(lambda: self.update_preview())
        self.mail_img_combo.currentIndexChanged.connect(lambda: self.update_preview())
        self.gift_img_combo.currentIndexChanged.connect(lambda: self.update_preview())
        self.font_size_spin.valueChanged.connect(lambda: self.update_preview())
        self.letter_spacing_spin.valueChanged.connect(lambda: self.update_preview())
        self.margin_top_spin.valueChanged.connect(lambda: self.update_preview())
        self.margin_bottom_spin.valueChanged.connect(lambda: self.update_preview())
        self.margin_h_spin.valueChanged.connect(lambda: self.update_preview())
        self.gift_img_size_spin.valueChanged.connect(lambda: self.update_preview())
        self.gift_text_fontsize_spin.valueChanged.connect(lambda: self.update_preview())

    def wrap_text(self, text, font, max_width, draw):
        # 自动换行，返回分行列表
        lines = []
        for paragraph in text.split('\n'):
            line = ''
            for char in paragraph:
                test_line = line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                w = bbox[2] - bbox[0]
                if w > max_width and line:
                    lines.append(line)
                    line = char
                else:
                    line = test_line
            lines.append(line)
        return lines

    def get_current_mail_image(self):
        mail_img_path = os.path.join(MAIL_IMG_DIR, self.mail_img_combo.currentText())
        base = Image.open(mail_img_path).convert("RGBA")
        draw = ImageDraw.Draw(base)
        font_size = self.font_size_spin.value()
        letter_spacing = self.letter_spacing_spin.value()
        margin_top = self.margin_top_spin.value()
        margin_bottom = self.margin_bottom_spin.value()
        margin_h = self.margin_h_spin.value()
        font = ImageFont.truetype(FONT_PATH, font_size)
        title = self.title_edit.text()
        body = self.body_edit.toPlainText()
        signature = self.signature_edit.text()
        gift_text = self.gift_text_edit.text()
        max_text_width = base.width - 2 * margin_h
        # 标题
        title_lines = self.wrap_text(title, font, max_text_width, draw)
        y = margin_top
        for line in title_lines:
            draw.text((margin_h, y), line, font=font, fill=(60, 40, 20))
            y += font_size + 4
        # 正文
        body_lines = self.wrap_text(body, font, max_text_width, draw)
        y += 10
        for line in body_lines:
            draw.text((margin_h, y), line, font=font, fill=(60, 40, 20))
            y += font_size + 4
        # 署名靠右
        sign_y = base.height - margin_bottom - 80
        sign_lines = self.wrap_text(signature, font, max_text_width, draw)
        for idx, line in enumerate(sign_lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            w = bbox[2] - bbox[0]
            draw.text((base.width - margin_h - w, sign_y + idx*(font_size+4)), line, font=font, fill=(60, 40, 20))
        # 礼物
        if self.gift_img_combo.currentText() != '无':
            gift_img_path = os.path.join(GIFT_IMG_DIR, self.gift_img_combo.currentText())
            icon_size = self.gift_img_size_spin.value()
            gift_img = Image.open(gift_img_path).convert("RGBA").resize((icon_size, icon_size))
            gift_text_fontsize = self.gift_text_fontsize_spin.value()
            gift_text_font = ImageFont.truetype(FONT_PATH, gift_text_fontsize)
            gift_text_gap = self.gift_text_gap_spin.value()
            gift_text_pos = self.gift_text_pos_combo.currentText()
            # 计算说明宽度
            gift_text_bbox = draw.textbbox((0, 0), gift_text, font=gift_text_font)
            gift_text_w = gift_text_bbox[2] - gift_text_bbox[0]
            total_w = gift_img.width + (gift_text_w if gift_text else 0) + (gift_text_gap if gift_text else 0)
            x_start = (base.width - total_w) // 2
            y_gift = base.height - margin_bottom - 30
            if gift_text and gift_text_pos == "图标前":
                # 说明-间距-图标
                draw.text((x_start, y_gift + (gift_img.height - gift_text_fontsize)//2), gift_text, font=gift_text_font, fill=(60, 40, 20))
                base.paste(gift_img, (x_start + gift_text_w + gift_text_gap, y_gift), gift_img)
            else:
                # 图标-间距-说明
                base.paste(gift_img, (x_start, y_gift), gift_img)
                draw.text((x_start + gift_img.width + gift_text_gap, y_gift + (gift_img.height - gift_text_fontsize)//2), gift_text, font=gift_text_font, fill=(60, 40, 20))
        return base

    def save_image(self):
        img = self.get_current_mail_image()
        path, _ = QFileDialog.getSaveFileName(self, "保存信件为图片", "mail.png", "PNG Files (*.png)")
        if path:
            img.save(path, format="PNG")

    def update_preview(self):
        # 让预览区自适应当前QLabel大小
        img = self.get_current_mail_image()
        label_size = self.preview_label.size()
        qimage = QImage(img.tobytes("raw", "RGBA"), img.width, img.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage).scaled(label_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MailGenerator()
    win.show()
    sys.exit(app.exec_())