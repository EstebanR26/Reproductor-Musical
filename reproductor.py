#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUSICREPRODUCER - Reproductor de Música Completo con Mejoras Avanzadas"""

import os, sys, json, random
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets, QtMultimedia

try:
    from mutagen import File as MutagenFile
    from mutagen.id3 import ID3, APIC
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False
    print("⚠️  Mutagen no disponible. Instala con: pip install mutagen")

APP_TITLE = "MUSICREPRODUCER"
PLAYLIST_EXT = ".m3ujson"
CONFIG_FILE = "config.json"

# Styles - Dark Theme
STYLE_DARK = """
QWidget{background-color:#0f1113;color:#d7eef0;font-family:"Segoe UI",Arial;font-size:13px}
QLineEdit#search{background-color:#111417;border:1px solid #153334;border-radius:18px;padding:8px 14px;color:#cfeff0;min-height:30px}
QLabel#app_title{color:#9ff5ff;font-weight:800;font-size:20px}
QGroupBox#player_card{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0d0e0f,stop:1 #0b0c0d);border:1px solid #132022;border-radius:12px;padding:12px}
QPushButton{background-color:#0f2b29;border:1px solid #03c4c4;color:#e9ffff;border-radius:22px;padding:8px 14px;min-height:38px}
QPushButton:hover{background-color:#025e5a}
QPushButton#big_play{background-color:#03c4c4;color:#001616;font-size:20px;font-weight:700;border-radius:30px;min-width:64px;min-height:64px}
QPushButton#round{background-color:transparent;border:1px solid #153334;border-radius:18px;min-width:36px;min-height:36px}
QListView{background:transparent;border:none;padding:6px;color:#dff9f9}
QListView::item{padding:10px;margin:2px}
QListView::item:selected{background:#032e2d;color:#bffff6}
QListView::item:hover{background:#021a1a}
QWidget#thumb_card{background-color:#0b0c0d;border:1px solid #162025;border-radius:10px;padding:6px}
QPushButton#clear_search{min-width:70px;border-radius:12px}
QLabel#track_title{color:#bff2f2;font-weight:800;font-size:18px}
QLabel#meta{color:#9acaca;font-size:12px}
QLabel#badge{background-color:#031615;border:1px solid #0a6a66;padding:4px 8px;border-radius:12px;color:#bff2f2;font-weight:700}
QSlider::groove:horizontal{border:1px solid #153334;height:6px;background:#111417;border-radius:3px}
QSlider::handle:horizontal{background:#03c4c4;border:1px solid #03c4c4;width:16px;margin:-5px 0;border-radius:8px}
QSlider::handle:horizontal:hover{background:#05e0e0}
"""

# Light Theme
STYLE_LIGHT = """
QWidget{background-color:#f5f7fa;color:#1a1d24;font-family:"Segoe UI",Arial;font-size:13px}
QLineEdit#search{background-color:#ffffff;border:1px solid #d0d5dd;border-radius:18px;padding:8px 14px;color:#1a1d24;min-height:30px}
QLabel#app_title{color:#0066cc;font-weight:800;font-size:20px}
QGroupBox#player_card{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #ffffff,stop:1 #f8f9fb);border:1px solid #e0e4eb;border-radius:12px;padding:12px}
QPushButton{background-color:#ffffff;border:1px solid #0066cc;color:#0066cc;border-radius:22px;padding:8px 14px;min-height:38px}
QPushButton:hover{background-color:#e6f2ff}
QPushButton#big_play{background-color:#0066cc;color:#ffffff;font-size:20px;font-weight:700;border-radius:30px;min-width:64px;min-height:64px}
QPushButton#round{background-color:transparent;border:1px solid #cbd2e0;border-radius:18px;min-width:36px;min-height:36px}
QListView{background:transparent;border:none;padding:6px;color:#1a1d24}
QListView::item{padding:10px;margin:2px}
QListView::item:selected{background:#e6f2ff;color:#0052a3}
QListView::item:hover{background:#f0f7ff}
QWidget#thumb_card{background-color:#ffffff;border:1px solid #e0e4eb;border-radius:10px;padding:6px}
QPushButton#clear_search{min-width:70px;border-radius:12px}
QLabel#track_title{color:#1a1d24;font-weight:800;font-size:18px}
QLabel#meta{color:#5a6372;font-size:12px}
QLabel#badge{background-color:#e6f2ff;border:1px solid #0066cc;padding:4px 8px;border-radius:12px;color:#0066cc;font-weight:700}
QSlider::groove:horizontal{border:1px solid #d0d5dd;height:6px;background:#e8ecf1;border-radius:3px}
QSlider::handle:horizontal{background:#0066cc;border:1px solid #0066cc;width:16px;margin:-5px 0;border-radius:8px}
QSlider::handle:horizontal:hover{background:#0052a3}
"""

# ============================================================================
# Utility Functions
# ============================================================================
def load_config():
    """Load app configuration"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        pass
    return {"favorites": {}, "volume": 100, "theme": "dark"}

def save_config(config):
    """Save app configuration"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def extract_metadata(filepath):
    """Extract metadata from audio file using mutagen"""
    if not MUTAGEN_AVAILABLE:
        return {"title": Path(filepath).stem, "artist": "Unknown", "album": "Unknown", "artwork": None}
    
    try:
        audio = MutagenFile(filepath, easy=True)
        if audio is None:
            return {"title": Path(filepath).stem, "artist": "Unknown", "album": "Unknown", "artwork": None}
        
        title = audio.get('title', [Path(filepath).stem])[0] if audio.get('title') else Path(filepath).stem
        artist = audio.get('artist', ['Unknown'])[0] if audio.get('artist') else "Unknown"
        album = audio.get('album', ['Unknown'])[0] if audio.get('album') else "Unknown"
        
        # Extract artwork
        artwork = None
        try:
            audio_full = MutagenFile(filepath)
            if hasattr(audio_full, 'tags'):
                for tag in audio_full.tags.values():
                    if isinstance(tag, APIC):
                        artwork = QtGui.QPixmap()
                        artwork.loadFromData(tag.data)
                        break
        except:
            pass
        
        return {"title": title, "artist": artist, "album": album, "artwork": artwork}
    except:
        return {"title": Path(filepath).stem, "artist": "Unknown", "album": "Unknown", "artwork": None}

# ============================================================================
# ProxyModel for Filtering
# ============================================================================
class FilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ""
        self.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)
    
    def setFilterText(self, text):
        self.filter_text = text.lower()
        self.invalidateFilter()
    
    def filterAcceptsRow(self, source_row, source_parent):
        if not self.filter_text:
            return True
        
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        item = source_model.data(index, QtCore.Qt.UserRole)
        
        if item:
            title = (item.get("title") or Path(item["path"]).stem).lower()
            artist = (item.get("artist") or "").lower()
            album = (item.get("album") or "").lower()
            return self.filter_text in title or self.filter_text in artist or self.filter_text in album
        return False

# ============================================================================
# PlaylistModel
# ============================================================================
class PlaylistModel(QtCore.QAbstractListModel):
    def __init__(self, items=None):
        super().__init__()
        self._items = items or []
    
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._items):
            return None
        
        item = self._items[index.row()]
        
        if role == QtCore.Qt.DisplayRole:
            title = item.get("title") or Path(item["path"]).stem
            artist = item.get("artist", "Unknown")
            dur = item.get("duration_ms")
            if dur:
                s = dur // 1000
                return f"{index.row()+1:2d}. {title} - {artist} [{s//60:02d}:{s%60:02d}]"
            return f"{index.row()+1:2d}. {title} - {artist}"
        
        if role == QtCore.Qt.UserRole:
            return item
        
        if role == QtCore.Qt.DecorationRole:
            if item.get("artwork"):
                return item["artwork"].scaled(48, 48, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        
        return None
    
    def rowCount(self, parent=QtCore.QModelIndex()):
        return len(self._items)
    
    def items(self):
        return list(self._items)
    
    def getItem(self, row):
        if 0 <= row < len(self._items):
            return self._items[row]
        return None
    
    def addItem(self, item, position=None):
        position = len(self._items) if position is None else position
        self.beginInsertRows(QtCore.QModelIndex(), position, position)
        self._items.insert(position, item)
        self.endInsertRows()
    
    def removeItem(self, row):
        if 0 <= row < len(self._items):
            self.beginRemoveRows(QtCore.QModelIndex(), row, row)
            self._items.pop(row)
            self.endRemoveRows()
            return True
        return False
    
    def setItems(self, items):
        self.beginResetModel()
        self._items = list(items)
        self.endResetModel()
    
    def clear(self):
        self.setItems([])
    
    def updateItem(self, row, item):
        if 0 <= row < len(self._items):
            self._items[row] = item
            idx = self.index(row)
            self.dataChanged.emit(idx, idx)

# ============================================================================
# PlaylistView with Context Menu
# ============================================================================
class PlaylistView(QtWidgets.QListView):
    deleteRequested = QtCore.pyqtSignal(int)
    
    def __init__(self, model):
        super().__init__()
        self.setModel(model)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.setUniformItemSizes(False)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)
    
    def showContextMenu(self, pos):
        index = self.indexAt(pos)
        if not index.isValid():
            return
        
        menu = QtWidgets.QMenu(self)
        delete_action = menu.addAction("🗑️ Eliminar")
        action = menu.exec_(self.mapToGlobal(pos))
        
        if action == delete_action:
            self.deleteRequested.emit(index.row())
    
    def dropEvent(self, event):
        super().dropEvent(event)
        try:
            self.model().layoutChanged.emit()
        except:
            pass

# ============================================================================
# WaveformWidget with Animation
# ============================================================================
class WaveformWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.is_playing = False
        self.animation_offset = 0
        self.setMinimumHeight(48)
        
        # Animation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(50)
    
    def setProgress(self, p):
        self.progress = max(0.0, min(1.0, p))
        self.update()
    
    def setPlaying(self, playing):
        self.is_playing = playing
    
    def animate(self):
        if self.is_playing:
            self.animation_offset = (self.animation_offset + 1) % 7
            self.update()
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        rect = self.rect()
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.fillRect(rect, QtGui.QColor(0,0,0,0))
        
        w, h = rect.width(), rect.height()
        bar_w, gap = 6, 4
        cols = max(1, w // (bar_w + gap))
        
        for i in range(cols):
            x = i * (bar_w + gap)
            # Animated height variation
            height_factor = 0.3 + 0.7 * (((i + self.animation_offset) % 7) / 6.0) if self.is_playing else 0.3 + 0.7 * ((i % 7) / 6.0)
            bar_h = int(h * height_factor)
            y = (h - bar_h) // 2
            
            is_active = x + bar_w/2 <= w * self.progress
            color = QtGui.QColor(3,196,196) if is_active else QtGui.QColor(8,40,38)
            
            painter.setBrush(color)
            painter.setPen(QtGui.QPen(color))
            painter.drawRoundedRect(x, y, bar_w, bar_h, 3, 3)

# ============================================================================
# Rotating Turntable Widget
# ============================================================================
class TurntableWidget(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotation = 0
        self.is_playing = False
        self.artwork = None
        self.setFixedSize(380, 300)
        
        # Rotation timer
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(30)
    
    def setArtwork(self, pixmap):
        self.artwork = pixmap
        self.update()
    
    def setPlaying(self, playing):
        self.is_playing = playing
    
    def rotate(self):
        if self.is_playing:
            self.rotation = (self.rotation + 2) % 360
            self.update()
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setRenderHint(QtGui.QPainter.SmoothPixmapTransform)
        
        rect = self.rect()
        center = rect.center()
        
        # Background gradient
        gradient = QtGui.QRadialGradient(center.x() * 0.7, center.y() * 0.7, min(rect.width(), rect.height()) * 0.8)
        gradient.setColorAt(0, QtGui.QColor(11, 11, 11))
        gradient.setColorAt(1, QtGui.QColor(19, 21, 22))
        painter.fillRect(rect, gradient)
        
        # Draw rotating disc
        painter.translate(center)
        painter.rotate(self.rotation)
        
        disc_size = 220
        disc_rect = QtCore.QRect(-disc_size//2, -disc_size//2, disc_size, disc_size)
        
        # Disc background
        disc_gradient = QtGui.QRadialGradient(0, 0, disc_size//2)
        disc_gradient.setColorAt(0, QtGui.QColor(30, 30, 30))
        disc_gradient.setColorAt(0.7, QtGui.QColor(15, 15, 15))
        disc_gradient.setColorAt(1, QtGui.QColor(5, 5, 5))
        painter.setBrush(disc_gradient)
        painter.setPen(QtGui.QPen(QtGui.QColor(40, 40, 40), 2))
        painter.drawEllipse(disc_rect)
        
        # Artwork or default center
        if self.artwork:
            artwork_size = 140
            artwork_rect = QtCore.QRect(-artwork_size//2, -artwork_size//2, artwork_size, artwork_size)
            painter.setClipRegion(QtGui.QRegion(artwork_rect, QtGui.QRegion.Ellipse))
            scaled_artwork = self.artwork.scaled(artwork_size, artwork_size, QtCore.Qt.KeepAspectRatioByExpanding, QtCore.Qt.SmoothTransformation)
            painter.drawPixmap(artwork_rect, scaled_artwork)
            painter.setClipping(False)
        else:
            # Center hole
            center_size = 60
            painter.setBrush(QtGui.QColor(20, 20, 20))
            painter.drawEllipse(-center_size//2, -center_size//2, center_size, center_size)
        
        # Grooves effect
        painter.setPen(QtGui.QPen(QtGui.QColor(25, 25, 25), 1))
        for r in range(75, disc_size//2, 8):
            painter.drawEllipse(-r, -r, r*2, r*2)

# ============================================================================
# MainWindow
# ============================================================================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(APP_TITLE)
        self.resize(1100, 680)
        
        # Load config
        self.config = load_config()
        
        # Multimedia
        self.player = QtMultimedia.QMediaPlayer()
        self.playlist = QtMultimedia.QMediaPlaylist()
        self.player.setPlaylist(self.playlist)
        self.player.setVolume(self.config.get("volume", 100))
        
        # Error handlers
        if hasattr(self.player, 'errorOccurred'):
            try: self.player.errorOccurred.connect(self.handlePlayerError)
            except: pass
        if hasattr(self.player, 'error'):
            try: self.player.error.connect(self.handlePlayerError)
            except: pass
        
        # State
        self.source_model = PlaylistModel()
        self.proxy_model = FilterProxyModel()
        self.proxy_model.setSourceModel(self.source_model)
        
        self.orig_order = []
        self.shuffle_on = False
        self.current_theme = self.config.get("theme", "dark")
        
        self.setupUi()
        self.applyTheme(self.current_theme)
        self.connectSignals()
        self.loadFavorites()
    
    def setupUi(self):
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QHBoxLayout(central)
        layout.setSpacing(18)
        layout.setContentsMargins(12,12,12,12)
        
        # Left column
        left_col = QtWidgets.QVBoxLayout()
        layout.addLayout(left_col, 2)
        
        # Header
        header = QtWidgets.QHBoxLayout()
        left_col.addLayout(header)
        title = QtWidgets.QLabel("MUSIC2D")
        title.setObjectName("app_title")
        header.addWidget(title, alignment=QtCore.Qt.AlignLeft)
        
        # Theme toggle
        self.btn_theme = QtWidgets.QPushButton("☀️" if self.current_theme == "dark" else "🌙")
        self.btn_theme.setObjectName("round")
        self.btn_theme.setToolTip("Cambiar tema")
        header.addWidget(self.btn_theme)
        
        header.addStretch()
        
        self.search_edit = QtWidgets.QLineEdit()
        self.search_edit.setObjectName("search")
        self.search_edit.setPlaceholderText("Buscar canciones, artistas, álbumes...")
        self.search_edit.setMinimumWidth(360)
        header.addWidget(self.search_edit)
        
        # Player card
        player_card = QtWidgets.QGroupBox()
        player_card.setObjectName("player_card")
        left_col.addWidget(player_card)
        pc_layout = QtWidgets.QVBoxLayout(player_card)
        
        # Top row with turntable + meta
        top_row = QtWidgets.QHBoxLayout()
        pc_layout.addLayout(top_row)
        
        self.turntable = TurntableWidget()
        top_row.addWidget(self.turntable)
        
        # Meta column
        meta_col = QtWidgets.QVBoxLayout()
        top_row.addLayout(meta_col, 1)
        
        self.track_title = QtWidgets.QLabel("Sin reproducción")
        self.track_title.setObjectName("track_title")
        self.track_title.setWordWrap(True)
        meta_col.addWidget(self.track_title)
        
        self.track_meta = QtWidgets.QLabel("Añade canciones para comenzar")
        self.track_meta.setObjectName("meta")
        self.track_meta.setWordWrap(True)
        meta_col.addWidget(self.track_meta)
        
        meta_col.addStretch()
        
        # Favorite row
        fav_row = QtWidgets.QHBoxLayout()
        meta_col.addLayout(fav_row)
        self.btn_fav = QtWidgets.QPushButton("♥")
        self.btn_fav.setObjectName("round")
        self.btn_fav.setToolTip("Marcar como favorito")
        self.lbl_fav_count = QtWidgets.QLabel("0")
        self.lbl_fav_count.setObjectName("badge")
        fav_row.addWidget(self.btn_fav)
        fav_row.addWidget(self.lbl_fav_count)
        fav_row.addStretch()
        
        # Waveform
        self.waveform = WaveformWidget()
        pc_layout.addWidget(self.waveform)
        
        # Time & slider
        time_row = QtWidgets.QHBoxLayout()
        pc_layout.addLayout(time_row)
        self.lbl_time = QtWidgets.QLabel("0:00 / 0:00")
        time_row.addWidget(self.lbl_time)
        time_row.addStretch()
        self.seek_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.seek_slider.setRange(0, 1000)
        time_row.addWidget(self.seek_slider)
        
        # Volume control
        vol_row = QtWidgets.QHBoxLayout()
        pc_layout.addLayout(vol_row)
        vol_row.addWidget(QtWidgets.QLabel("🔊"))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.config.get("volume", 100))
        self.volume_slider.setMaximumWidth(150)
        vol_row.addWidget(self.volume_slider)
        self.lbl_volume = QtWidgets.QLabel(f"{self.config.get('volume', 100)}%")
        vol_row.addWidget(self.lbl_volume)
        vol_row.addStretch()
        
        # Transport controls
        controls = QtWidgets.QHBoxLayout()
        pc_layout.addLayout(controls)
        
        self.btn_shuffle = QtWidgets.QPushButton("🔀")
        self.btn_shuffle.setObjectName("round")
        self.btn_shuffle.setToolTip("Aleatorio")
        self.btn_prev = QtWidgets.QPushButton("⏮")
        self.btn_prev.setObjectName("round")
        self.btn_prev.setToolTip("Anterior")
        self.btn_play = QtWidgets.QPushButton("▶")
        self.btn_play.setObjectName("big_play")
        self.btn_play.setToolTip("Reproducir/Pausar")
        self.btn_next = QtWidgets.QPushButton("⏭")
        self.btn_next.setObjectName("round")
        self.btn_next.setToolTip("Siguiente")
        self.btn_repeat = QtWidgets.QPushButton("🔁")
        self.btn_repeat.setObjectName("round")
        self.btn_repeat.setToolTip("Repetir")
        
        for btn in [self.btn_shuffle, self.btn_prev, self.btn_play, self.btn_next, self.btn_repeat]:
            controls.addWidget(btn)
        
        # Lower operations
        lower_ops = QtWidgets.QHBoxLayout()
        left_col.addLayout(lower_ops)
        self.btn_add = QtWidgets.QPushButton("➕ Añadir")
        self.btn_add.setObjectName("round")
        self.btn_load = QtWidgets.QPushButton("📂 Cargar lista")
        self.btn_load.setObjectName("round")
        self.btn_save = QtWidgets.QPushButton("💾 Guardar lista")
        self.btn_save.setObjectName("round")
        lower_ops.addWidget(self.btn_add)
        lower_ops.addWidget(self.btn_load)
        lower_ops.addWidget(self.btn_save)
        lower_ops.addStretch()
        
        # Right column
        right_col = QtWidgets.QVBoxLayout()
        layout.addLayout(right_col, 1)
        
        # Playlist header
        playlist_header = QtWidgets.QHBoxLayout()
        right_col.addLayout(playlist_header)
        playlist_label = QtWidgets.QLabel("Reproduciendo ahora")
        playlist_label.setStyleSheet("font-weight:700; font-size:15px;")
        playlist_header.addWidget(playlist_label)
        playlist_header.addStretch()
        
        self.lbl_track_count = QtWidgets.QLabel("0 pistas")
        self.lbl_track_count.setObjectName("meta")
        playlist_header.addWidget(self.lbl_track_count)
        
        # Playlist view
        self.playlist_view = PlaylistView(self.proxy_model)
        right_col.addWidget(self.playlist_view)
        
        # Status bar
        self.status = self.statusBar()
        self.status.showMessage("Listo")
    
    def connectSignals(self):
        # Buttons
        self.btn_add.clicked.connect(self.addFiles)
        self.btn_load.clicked.connect(self.loadPlaylist)
        self.btn_save.clicked.connect(self.savePlaylist)
        self.btn_play.clicked.connect(self.togglePlay)
        self.btn_prev.clicked.connect(self.playPrevious)
        self.btn_next.clicked.connect(self.playNext)
        self.btn_shuffle.clicked.connect(self.toggleShuffle)
        self.btn_repeat.clicked.connect(self.toggleRepeat)
        self.btn_fav.clicked.connect(self.toggleFavorite)
        self.btn_theme.clicked.connect(self.toggleTheme)
        
        # Player
        self.player.positionChanged.connect(self.onPositionChanged)
        self.player.durationChanged.connect(self.onDurationChanged)
        self.player.stateChanged.connect(self.onStateChanged)
        self.playlist.currentIndexChanged.connect(self.onCurrentIndexChanged)
        
        # Sliders
        self.seek_slider.sliderMoved.connect(self.seekSliderMoved)
        self.volume_slider.valueChanged.connect(self.onVolumeChanged)
        
        # Search
        self.search_edit.textChanged.connect(self.onSearch)
        
        # Playlist view
        self.playlist_view.doubleClicked.connect(self.onItemDoubleClicked)
        self.playlist_view.deleteRequested.connect(self.deleteTrack)
        
        # Shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence("Space"), self, activated=self.togglePlay)
        QtWidgets.QShortcut(QtGui.QKeySequence("Right"), self, activated=self.playNext)
        QtWidgets.QShortcut(QtGui.QKeySequence("Left"), self, activated=self.playPrevious)
        QtWidgets.QShortcut(QtGui.QKeySequence("Delete"), self, activated=self.deleteCurrentTrack)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+O"), self, activated=self.addFiles)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self, activated=self.savePlaylist)
        QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+L"), self, activated=self.loadPlaylist)
    
    def applyTheme(self, theme):
        """Apply dark or light theme"""
        if theme == "dark":
            self.setStyleSheet(STYLE_DARK)
        else:
            self.setStyleSheet(STYLE_LIGHT)
    
    def toggleTheme(self):
        """Toggle between dark and light theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self.applyTheme(self.current_theme)
        self.btn_theme.setText("☀️" if self.current_theme == "dark" else "🌙")
        self.config["theme"] = self.current_theme
        save_config(self.config)
        self.status.showMessage(f"Tema {'oscuro' if self.current_theme == 'dark' else 'claro'} activado", 2000)
    
    def loadFavorites(self):
        """Load favorite tracks count"""
        favorites = self.config.get("favorites", {})
        self.lbl_fav_count.setText(str(len(favorites)))
    
    # Playlist actions
    def addFiles(self):
        """Add audio files with metadata extraction"""
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(
            self, "Seleccionar archivos de audio", 
            os.getcwd(), 
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a)"
        )
        if not files:
            return
        
        # Progress dialog for large file sets
        progress = QtWidgets.QProgressDialog("Extrayendo metadata...", "Cancelar", 0, len(files), self)
        progress.setWindowModality(QtCore.Qt.WindowModal)
        
        added = 0
        for i, p in enumerate(files):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Procesando: {Path(p).name}")
            QtWidgets.QApplication.processEvents()
            
            try:
                metadata = extract_metadata(p)
                item = {
                    "path": p,
                    "title": metadata["title"],
                    "artist": metadata["artist"],
                    "album": metadata["album"],
                    "artwork": metadata["artwork"],
                    "duration_ms": None,
                    "is_favorite": p in self.config.get("favorites", {})
                }
                self.source_model.addItem(item)
                self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(p)))
                self.orig_order.append(p)
                added += 1
            except Exception as e:
                print(f"Error adding {p}: {e}")
        
        progress.setValue(len(files))
        self.updateTrackCount()
        self.status.showMessage(f"{added} pistas añadidas", 3000)
    
    def loadPlaylist(self):
        """Load playlist from file"""
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Cargar playlist", 
            os.getcwd(), 
            f"Playlist (*{PLAYLIST_EXT})"
        )
        if not path:
            return
        
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            items = data.get("items", [])
            self.orig_order = data.get("orig_order", [])
            
            # Clear current playlist
            self.source_model.clear()
            self.playlist.clear()
            
            # Reload with metadata
            progress = QtWidgets.QProgressDialog("Cargando playlist...", "Cancelar", 0, len(items), self)
            progress.setWindowModality(QtCore.Qt.WindowModal)
            
            loaded = 0
            for i, item in enumerate(items):
                if progress.wasCanceled():
                    break
                
                progress.setValue(i)
                filepath = item.get("path")
                
                if not filepath or not os.path.exists(filepath):
                    continue
                
                # Re-extract metadata to ensure artwork is loaded
                metadata = extract_metadata(filepath)
                item.update(metadata)
                item["is_favorite"] = filepath in self.config.get("favorites", {})
                
                self.source_model.addItem(item)
                self.playlist.addMedia(QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(filepath)))
                loaded += 1
            
            progress.setValue(len(items))
            self.updateTrackCount()
            self.status.showMessage(f"Playlist cargada: {loaded} pistas", 3000)
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo cargar la playlist:\n{e}")
    
    def savePlaylist(self):
        """Save current playlist"""
        if self.source_model.rowCount() == 0:
            self.status.showMessage("No hay pistas para guardar", 3000)
            return
        
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Guardar playlist", 
            os.getcwd(), 
            f"Playlist (*{PLAYLIST_EXT})"
        )
        if not path:
            return
        
        if not path.endswith(PLAYLIST_EXT):
            path += PLAYLIST_EXT
        
        # Don't save artwork pixmaps, only paths
        items = []
        for item in self.source_model.items():
            save_item = {k: v for k, v in item.items() if k != "artwork"}
            items.append(save_item)
        
        payload = {"items": items, "orig_order": self.orig_order}
        
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, indent=2, ensure_ascii=False)
            self.status.showMessage("Playlist guardada", 3000)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Error guardando playlist:\n{e}")
    
    def deleteTrack(self, row):
        """Delete track from playlist"""
        # Get source row from proxy
        proxy_index = self.proxy_model.index(row, 0)
        source_index = self.proxy_model.mapToSource(proxy_index)
        source_row = source_index.row()
        
        item = self.source_model.getItem(source_row)
        if not item:
            return
        
        title = item.get("title", "Unknown")
        reply = QtWidgets.QMessageBox.question(
            self, "Eliminar pista",
            f"¿Eliminar '{title}' de la lista?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # Remove from playlist
            self.playlist.removeMedia(source_row)
            # Remove from model
            self.source_model.removeItem(source_row)
            # Update orig_order
            if source_row < len(self.orig_order):
                self.orig_order.pop(source_row)
            
            self.updateTrackCount()
            self.status.showMessage("Pista eliminada", 2000)
    
    def deleteCurrentTrack(self):
        """Delete currently selected track"""
        index = self.playlist_view.currentIndex()
        if index.isValid():
            self.deleteTrack(index.row())
    
    def updateTrackCount(self):
        """Update track count label"""
        count = self.source_model.rowCount()
        self.lbl_track_count.setText(f"{count} pista{'s' if count != 1 else ''}")
    
    # Playback controls
    def togglePlay(self):
        """Toggle play/pause"""
        if self.player.state() == QtMultimedia.QMediaPlayer.PlayingState:
            self.player.pause()
            self.btn_play.setText("▶")
        else:
            if self.playlist.mediaCount() == 0:
                self.status.showMessage("Lista vacía. Añade pistas primero.", 3000)
                return
            if self.playlist.currentIndex() == -1:
                self.playlist.setCurrentIndex(0)
            self.player.play()
            self.btn_play.setText("⏸")
    
    def playNext(self):
        """Play next track"""
        if self.playlist.mediaCount() == 0:
            return
        if self.shuffle_on:
            self.playlist.setCurrentIndex(random.randrange(self.playlist.mediaCount()))
        else:
            self.playlist.next()
    
    def playPrevious(self):
        """Play previous track"""
        if self.playlist.mediaCount() > 0:
            self.playlist.previous()
    
    def toggleShuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_on = not self.shuffle_on
        self.btn_shuffle.setStyleSheet("background-color: #034f4c;" if self.shuffle_on else "")
        self.status.showMessage("Aleatorio activado" if self.shuffle_on else "Aleatorio desactivado", 2000)
    
    def toggleRepeat(self):
        """Cycle through repeat modes"""
        cur = self.playlist.playbackMode()
        if cur == QtMultimedia.QMediaPlaylist.Loop:
            self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.CurrentItemOnce)
            self.btn_repeat.setText("🔂")
            self.status.showMessage("Repetir una vez", 2000)
        elif cur == QtMultimedia.QMediaPlaylist.CurrentItemOnce:
            self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.Sequential)
            self.btn_repeat.setText("➡️")
            self.status.showMessage("Sin repetición", 2000)
        else:
            self.playlist.setPlaybackMode(QtMultimedia.QMediaPlaylist.Loop)
            self.btn_repeat.setText("🔁")
            self.status.showMessage("Repetir todo", 2000)
    
    def toggleFavorite(self):
        """Toggle favorite for current track"""
        idx = self.playlist.currentIndex()
        if idx < 0:
            return
        
        item = self.source_model.getItem(idx)
        if not item:
            return
        
        path = item.get("path")
        favorites = self.config.get("favorites", {})
        
        if path in favorites:
            del favorites[path]
            self.status.showMessage("Eliminado de favoritos", 2000)
            item["is_favorite"] = False
        else:
            favorites[path] = {
                "title": item.get("title"),
                "artist": item.get("artist")
            }
            self.status.showMessage("Añadido a favoritos", 2000)
            item["is_favorite"] = True
        
        self.config["favorites"] = favorites
        save_config(self.config)
        self.lbl_fav_count.setText(str(len(favorites)))
        self.source_model.updateItem(idx, item)
    
    # Player events
    def onPositionChanged(self, pos):
        """Update position slider and time"""
        dur = max(1, self.player.duration())
        val = int(pos * 1000 / dur) if dur else 0
        self.seek_slider.blockSignals(True)
        self.seek_slider.setValue(val)
        self.seek_slider.blockSignals(False)
        self.waveform.setProgress(pos/dur if dur > 0 else 0)
        self.updateTimeLabel(pos, dur)
    
    def onDurationChanged(self, dur):
        """Store duration in model"""
        idx = self.playlist.currentIndex()
        if 0 <= idx < self.source_model.rowCount():
            item = self.source_model.getItem(idx)
            if item and not item.get("duration_ms"):
                item["duration_ms"] = dur
                self.source_model.updateItem(idx, item)
        self.updateTimeLabel(self.player.position(), dur)
    
    def onStateChanged(self, state):
        """Update UI based on player state"""
        is_playing = state == QtMultimedia.QMediaPlayer.PlayingState
        self.waveform.setPlaying(is_playing)
        self.turntable.setPlaying(is_playing)
        
        if state == QtMultimedia.QMediaPlayer.StoppedState:
            self.btn_play.setText("▶")
    
    def updateTimeLabel(self, pos, dur):
        """Format and update time label"""
        def fmt(ms):
            s = max(0, ms // 1000)
            return f"{s//60}:{s%60:02d}"
        self.lbl_time.setText(f"{fmt(pos)} / {fmt(dur)}")
    
    def seekSliderMoved(self, v):
        """Seek to position"""
        dur = self.player.duration()
        if dur > 0:
            self.player.setPosition(int(v / 1000 * dur))
    
    def onVolumeChanged(self, value):
        """Update volume"""
        self.player.setVolume(value)
        self.lbl_volume.setText(f"{value}%")
        self.config["volume"] = value
        save_config(self.config)
    
    def onCurrentIndexChanged(self, idx):
        """Update UI when track changes"""
        if idx < 0:
            return
        
        item = self.source_model.getItem(idx)
        if not item:
            return
        
        title = item.get("title", "Unknown")
        artist = item.get("artist", "Unknown")
        album = item.get("album", "Unknown")
        
        self.track_title.setText(title)
        self.track_meta.setText(f"{artist} • {album}")
        
        # Update artwork
        if item.get("artwork"):
            self.turntable.setArtwork(item["artwork"])
        else:
            self.turntable.setArtwork(None)
        
        # Set selection on playlist view
        proxy_index = self.proxy_model.mapFromSource(self.source_model.index(idx))
        self.playlist_view.setCurrentIndex(proxy_index)
        
        # Update favorite button state
        is_fav = item.get("is_favorite", False)
        self.btn_fav.setStyleSheet("background-color: #8b0000;" if is_fav else "")
    
    def onItemDoubleClicked(self, proxy_index):
        """Play track on double click"""
        if not proxy_index.isValid():
            return
        
        source_index = self.proxy_model.mapToSource(proxy_index)
        row = source_index.row()
        
        self.playlist.setCurrentIndex(row)
        self.player.play()
        self.btn_play.setText("⏸")
    
    def onSearch(self, text):
        """Filter playlist by search text"""
        self.proxy_model.setFilterText(text)
        
        if text.strip():
            self.status.showMessage(f"Mostrando {self.proxy_model.rowCount()} resultados", 2000)
        else:
            self.status.showMessage("Mostrando todas las pistas", 2000)
    
    def handlePlayerError(self, *args):
        """Handle playback errors"""
        try:
            err = self.player.errorString()
        except:
            err = "Error de reproducción desconocido"
        
        QtWidgets.QMessageBox.warning(self, "Error de Reproducción", 
            f"No se puede reproducir el archivo:\n{err}")
        self.status.showMessage("Error de reproducción", 5000)
    
    def closeEvent(self, event):
        """Save config on close"""
        save_config(self.config)
        event.accept()

# ============================================================================
# MAIN
# ============================================================================
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName(APP_TITLE)
    app.setOrganizationName("MUSICREPRODUCER")
    
    # Set app icon if available
    # app.setWindowIcon(QtGui.QIcon("icon.png"))
    
    win = MainWindow()
    win.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()