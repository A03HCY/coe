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

$.extend({
    info: (info) => {
        mdui.snackbar({
            message: info,
            closeOnOutsideClick: true
        });
    },
    online_clients: (func_suc, func_err) => {
        $.ajax({
            method: 'GET',
            url: '/online_clients',
            success: function (response) {
                if (response)
                    try {
                        online_clients = response;
                        if (func_suc != null) func_suc();
                        console.log('Get online_clients successful');
                    } catch (err) {
                        online_clients = {};
                        console.log('Unable to get online_clients');
                        if (func_err != null) func_err();
                    }
            }
        });
    },
    reload_select: (id) => {
        $.online_clients(
            () => {
                let select_html = '';
                for (let client_uuid in online_clients) {
                    let client_html = selects.replace('UUID', client_uuid).replace('NAME', client_uuid);
                    select_html += client_html;
                }
                $(id).html(select_html);
                $.info('刷新完成')
            }, () => { }
        );
    },
    is_online: (uuid) => {
        if (uuid == '') {
            $.info('未选择设备')
            return false;
        }
        if (!(uuid in online_clients)) {
            $.info('设备离线')
            return false;
        }
        return true;
    },
    bytes_resize: (size) => {
        if (!size) return '';
        var num = 1024.00; //byte
        if (size < num)
            return size + ' B';
        if (size < Math.pow(num, 2))
            return (size / num).toFixed(2) + ' KB'; //kb
        if (size < Math.pow(num, 3))
            return (size / Math.pow(num, 2)).toFixed(2) + ' MB'; //M
        if (size < Math.pow(num, 4))
            return (size / Math.pow(num, 3)).toFixed(2) + ' G'; //G
        return (size / Math.pow(num, 4)).toFixed(2) + ' T'; //T
    }
});

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

// Control 区域函数

function screenshot() {
    let client_uuid = $('#control-select').val();
    if (!$.is_online(client_uuid)) return;
    let url = '/screenshot?' + $.param({ uuid: client_uuid, time: Date.parse(new Date()) });
    $('#screenshot').attr('src', url);
}