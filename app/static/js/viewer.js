let data = $.diff_page()

if (data.file_name == undefined) {
    /*
    mdui.alert({
        headline: '没有选择指定的文件预览',
        description: '请重新选择文件',
        confirmText: '了解',
        icon: 'error_outline',
        onConfirm: () => window.close()
    });
    throw 'no data'
    */
} else {
    data.extension = data.file_name.slice(data.file_name.lastIndexOf('.'));
    $('#title').html(data.file_name)
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
            $.change_font('page', 'Consolas')
        })
    })
}

// 功能函数

function print_page() {
    $('.bar').toggleClass('hidden')
    window.print()
    $('.bar').toggleClass('hidden')
}

const func_ext = {
    markdown: ['.md', '.txt'],
    code: Object.keys(language_map)
}

let done = false
for (let func in func_ext) {
    if (func_ext[func].includes(data.extension)) {
        try {
            window[func]()
            done = true
            $.info('解析完成')
        } catch (e) {}
        break
    }
}
if (!done) {
    $.info('无法解析此文件')
    $('#page').html(`<mdui-icon class="center-element" name="error_outline" style="font-size: 48px"></mdui-icon>`)
}