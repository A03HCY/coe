const icon_map = {
    'audio_file--outlined': ['.mp3', '.wav', '.ogg'],
    'video_file--outlined': ['.mp4', '.flv'],
    'photo--outlined': ['.png', '.jpg', '.jpeg', '.svg'],
    'book--outlined': ['.txt', '.md'],
    'font_download--outlined': ['.ttf'],
    'link--outlined': ['.lnk'],
    'folder_zip--outlined': ['.zip', '.rar', '.7z'],
    'apps--outlined': ['.app', '.exe', '.msi']
}

const icon_color_map = {
    'audio_file--outlined': '--mdui-color-error-dark',
    'video_file--outlined': '--mdui-color-surface-tint-color-light',
    'photo--outlined': '--mdui-color-tertiary-dark',
    'book--outlined': '--mdui-color-primary',
    'font_download--outlined': '--mdui-color-secondary-light',
    'link--outlined': '--mdui-color-surface-tint-color-light',
    'folder_zip--outlined': '--mdui-color-on-surface-variant-dark',
    'apps--outlined': '--mdui-color-tertiary-container-dark'
}

const file_preview = [].concat(
    icon_map['audio_file--outlined'],
    icon_map['video_file--outlined'],
    icon_map['photo--outlined'],
    icon_map['book--outlined']
);