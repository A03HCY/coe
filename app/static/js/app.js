const selects = '<mdui-menu-item icon="link" value="UUID">NAME</mdui-menu-item>';
const setting = document.querySelector("#setting-panel");

let online_clients = {};

$('#settings').on('click', (e) => { setting.open = true });
$('#setting_close').on('click', (e) => { setting.open = false });

$('#index').on('click', (e) => {
    $('#index-panel').removeClass('hidden');
    $('#trans-panel').addClass('hidden');
    $('#control-panel').addClass('hidden');
});

$('#trans').on('click', (e) => {
    $('#trans-panel').removeClass('hidden');
    $('#index-panel').addClass('hidden');
    $('#control-panel').addClass('hidden');
});

$('#control').on('click', (e) => {
    $('#control-panel').removeClass('hidden');
    $('#trans-panel').addClass('hidden');
    $('#index-panel').addClass('hidden');
});

// 其他函数

let icon_map = {
    'audio_file--outlined': ['.mp3', '.wav', '.ogg'],
    'video_file--outlined': ['.mp4', '.flv'],
    'photo--outlined': ['.png', '.jpg', '.jpeg', '.svg'],
    'book--outlined': ['.txt', '.md'],
    'font_download--outlined': ['.tff'],
    'link--outlined': ['.lnk'],
    'folder_zip--outlined': ['.zip', '.rar', '.7z'],
    'apps--outlined': ['.app', '.exe', '.msi']
}

$.load_script(
    '/static.js/language_map.js', () => {
        icon_map['code'] = Object.keys(language_map)
    }
)

function find_icon(extn) {
    extn = $.file_extension(extn)
    for (let icon in icon_map) {
        if (icon_map[icon].includes(extn)) {
            return icon
        }
    }
    return 'insert_drive_file--outlined'
}

// Panel 区域函数

function show_info() {
    let client_uuid = $('#index-select').val();
    if (!$.is_online(client_uuid)) return;
    let client_info = online_clients[client_uuid][1];
    $('#computer-name').html(client_info['Computer Name']);
    $('#computer-system').html(client_info['Operating System']);
    $('#computer-version').html(client_info['OS Version']);
    $('#computer-architecture').html(String(client_info['Architecture']));
    $('#computer-cpu').html(client_info['Processor']);
    $('#computer-frequency').html(client_info['Frequency']);
    $('#computer-memory').html($.bytes_resize(client_info['Memory']));
    $.info('完成')
}

// Transfer 区域函数

function generate_folder_files(json_data) {
    let html = '<mdui-list>';
    // 生成文件夹项的HTML代码
    for (let folder_name in json_data[0]) {
        let folder = json_data[0][folder_name];
        html += `<mdui-list-item name="${folder_name}" onclick="into_directory(this)" alignment="center" end-icon="arrow_right">`;
        html += `  ${folder_name}`;
        html += `  <mdui-icon slot="icon" name="folder--outlined"></mdui-icon>`;
        html += `</mdui-list-item>`;
    }
    // 生成文件项的HTML代码
    for (let file_name in json_data[1]) {
        let file = json_data[1][file_name];
        let icon = find_icon(file_name)
        let description = `${file['date']}&nbsp;&nbsp;&nbsp;|&nbsp;&nbsp;&nbsp;${$.bytes_resize(file['size']).replace(' ', '')}`;
        html += `<mdui-list-item alignment="center" name="${file_name}" description="${description}" nonclickable="true" end-icon="arrow_right">`;
        html += `  ${file_name}`;
        html += `  <mdui-icon slot="icon" name="${icon}"></mdui-icon>`;
        if (file['size'] <= 30 * 1024 * 1024) {
            html += `  <mdui-button-icon onclick="file_trans(this, true)" slot="end-icon" icon="file_open--outlined"></mdui-button-icon>`;
        }
        html += `  <mdui-button-icon onclick="delet(this)" slot="end-icon" icon="delete_outlined"></mdui-button-icon>`;
        html += `  <mdui-button-icon onclick="rename(this)" slot="end-icon" icon="drive_file_rename_outline"></mdui-button-icon>`;
        html += `  <mdui-button-icon onclick="file_trans(this)" slot="end-icon" icon="file_download--outlined"></mdui-button-icon>`;
        html += `</mdui-list-item>`;
    }
    html += '</mdui-list>';
    return html;
}

function generate() {
    $('#trans-dir').val($.join_path('./', $('#trans-dir').val()));
    let client_uuid = $('#trans-select').val();
    let directory = $('#trans-dir').val();
    $('#trans-folder-files').html(`<mdui-circular-progress class="bar-center-element"></mdui-circular-progress>`);
    $.ajax({
        method: 'GET',
        url: '/api/folder_files?uuid=' + client_uuid + '&directory=' + $.base64_encode(directory),
        success: function (response) {
            response = JSON.parse(response);
            $.info('请求成功');
            $('#trans-folder-files').html(generate_folder_files(response.file_list));
        }
    });
}

function into_directory(self) {
    let dir = $('#trans-dir');
    self = $(self);
    dir.val($.join_path(dir.val(), self.attr('name')))
    generate()
}

function parent_folder() {
    let dir = $('#trans-dir');
    dir.val($.join_path(dir.val(), '..'))
    generate()
}

function file_trans(self, view) {
    self = $(self).parent();
    let size = self.attr('description');
    let name = self.attr('name');
    let client_uuid = $('#trans-select').val();
    let directory = $.join_path($('#trans-dir').val(), name)
    let api = '/api/trans_file?uuid=' + client_uuid + '&directory=' + $.base64_encode(directory)
    if (view) {
        let client_info = online_clients[client_uuid][1];
        let data = {
            'file_name': name,
            'size': size.split('|')[1].replace(/\s/g, ''),
            'directory': directory,
            'client_uuid': client_uuid,
            'url': api,
            'client_info': client_info
        }
        $.diff_page('/view', data)
    } else {
        $.download_file(url, name)
    }
}

function delet(self) {
    self = $(self).parent();
    let client_uuid = $('#trans-select').val();
    let client_info = online_clients[client_uuid][1];
    let name = self.attr('name');
    let directory = $.join_path($('#trans-dir').val(), name)
    let api = '/api/remove_file?uuid=' + client_uuid + '&directory=' + $.base64_encode(directory);
    mdui.confirm({
        icon: 'delete_outlined',
        headline: `确定要从 ${client_info['Computer Name']} 上删除 '${name}' 文件吗?`,
        description: '删除后文件将无法恢复',
        confirmText: '确认',
        cancelText: '取消',
        onConfirm: () => {
            $.ajax({
                method: 'GET',
                url: api,
                success: generate()
            });
        },
    });
}

function rename(self) {
    self = $(self).parent()
    let client_uuid = $('#trans-select').val()
    let client_info = online_clients[client_uuid][1]
    let name = self.attr('name')
    let directory = $.join_path($('#trans-dir').val(), name)
    mdui.prompt({
        icon: 'drive_file_rename_outline',
        headline: `在 ${client_info['Computer Name']} 上重命名 '${name}' 文件`,
        confirmText: "确定",
        cancelText: "取消",
        onConfirm: (value) => {
            let api = '/api/rename_path_file?uuid=' + client_uuid + '&directory=' + $.base64_encode(directory) + '&new=' + $.base64_encode(value);
            $('#trans-folder-files').html(`<mdui-circular-progress class="bar-center-element"></mdui-circular-progress>`);
            $.ajax({
                method: 'GET',
                url: api,
                success: () => {
                    $.time(() => {
                        generate()
                    }, 100)
                }
            });
        },
    });
}

// Control 区域函数

const slider = document.querySelector("#stream_quality");
slider.labelFormatter = (value) => `传输质量 ${value}%`;

function screenshot() {
    let client_uuid = $('#control-select').val();
    let url = '/api/screenshot?' + $.param({ uuid: client_uuid, time: Date.parse(new Date()) });
    $('#screenshot').attr('src', url);
}

function screenshot_stream() {
    let client_uuid = $('#control-select').val();
    let stream_quality = $('#stream_quality').val();
    let url = '/api/screen_stream?' + $.param({ uuid: client_uuid, quality: stream_quality, time: Date.parse(new Date()) });
    $('#screenshot').attr('src', url);
}