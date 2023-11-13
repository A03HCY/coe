let data = $.diff_page()
let audio_player, video_player

if (data.file_name == undefined || data == {}) {
    mdui.alert({
        headline: '没有选择指定的文件预览',
        description: '请重新选择文件',
        confirmText: '了解',
        icon: 'error_outline',
        onConfirm: () => {
            $('#page').html(`<mdui-icon class="center-element" name="error_outline" style="font-size: 48px"></mdui-icon>`)
            window.close()
        }
    });
    throw 'no data'
} else {
    data.extension = data.file_name.slice(data.file_name.lastIndexOf('.'));
    $('#title').html(data.file_name)
    $.title(`${data.file_name} | ${data.client_info['Computer Name']}`)
}

function alert_size() {
    mdui.alert({
        headline: '要预览的文件过大，无法在线查看',
        description: '若要查看文件内容，请下载文件',
        confirmText: '了解',
        icon: 'error_outline',
        onConfirm: () => {
            $('#page').html(`<mdui-icon class="center-element" name="error_outline" style="font-size: 48px"></mdui-icon>`)
            window.close()
        }
    });
}

let unit = $.extract_unit(data.size)
let size = parseInt($.extract_integer_part(data.size))

if (['B', 'KB'].includes(unit)) { } else if (unit == 'MB') {
    if (size > 30){
        alert_size()
        throw 'too big'
    }
} else {
    alert_size()
    throw 'too big'
}

function read(type, func) {
    $.ajax({
        url: data.url,
        dataType: type,
        success: func
    });
}

// 渲染函数

function markdown() {
    read('text', (respons) => {
        $('#page').html(marked(respons));
    })
}

function code() {
    let map = language_map[data.extension]
    $.load_script('/static/highlight/languages/NAME.min.js'.replace('NAME', map), () => {
        read('text', (respon) => {
            $('#page').html(`<pre><code class="LAN">`.replace('LAN', map) + respon + `</code></pre>`)
            hljs.highlightAll()
        })
    })
}

function audio() {
    $.ajax({
        url: data.url,
        method: 'GET',
        xhrFields: {
            responseType: 'blob'
        },
        success: function (data) {
            let html = `<audio id="audio_player" class="center-element" style="width=100%" controls><source type="audio/mpeg">Your browser does not support this audio format.</audio>`
            $('#page').html(html)
            audio_player = document.getElementById('audio_player');
            const audioURL = URL.createObjectURL(data);
            audio_player.src = audioURL;
            audio_player.play();
        },
        error: function (xhr, status, error) {
            $.info('请求失败: ' + error);
        }
    });
}

function video() {
    $.ajax({
        url: data.url,
        method: 'GET',
        xhrFields: {
            responseType: 'blob'
        },
        success: function (data) {
            let html = `<video id="video_player" controls></video>`
            $('#page').html(html)
            const videoURL = URL.createObjectURL(data);
            $.load_video('video_player', 'mp4', videoURL)
        },
        error: function (xhr, status, error) {
            $.info('请求失败: ' + error);
        }
    });
}
// 功能函数

function print_page() {
    $('.bar').toggleClass('hidden')
    window.print()
    $('.bar').toggleClass('hidden')
}

const func_ext = {
    markdown: ['.md', '.txt'],
    code: Object.keys(language_map),
    audio: ['.mp3', '.wav', '.ogg'],
    video: ['.flv']
}

let done = false
for (let func in func_ext) {
    if (func_ext[func].includes(data.extension)) {
        try {
            window[func]()
            done = true
            $.info('解析完成')
        } catch (e) { }
        break
    }
}
if (!done) {
    $.info('无法解析此文件')
    $('#page').html(`<mdui-icon class="center-element" name="error_outline" style="font-size: 48px"></mdui-icon>`)
}