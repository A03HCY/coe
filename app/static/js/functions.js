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
    online_clients: (func_suc, func_err) => {
        $.ajax({
            method: 'GET',
            url: '/online_clients',
            success: function (response) {
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
    }
});

$.extend({
    reload_select: (id) => {
        $.online_clients(
            () => {
                let select_html = '';
                for (let client_uuid in online_clients) {
                    let client_html = selects.replace('UUID', client_uuid).replace('NAME', client_uuid);
                    select_html += client_html;
                }
                $(id).html(select_html);
                mdui.snackbar({
                    message: "刷新完成",
                    closeOnOutsideClick: true
                });
            }, () => {}
        );
    }
});

// Transfer 区域函数
