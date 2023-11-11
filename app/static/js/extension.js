let $ = mdui.$;

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
            url: '/api/online_clients',
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
            }, () => {
                $.info('无法获取数据')
            }
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
        let num = 1024.00; //byte
        if (size < num)
            return size + ' B';
        if (size < Math.pow(num, 2))
            return (size / num).toFixed(2) + ' KB'; //kb
        if (size < Math.pow(num, 3))
            return (size / Math.pow(num, 2)).toFixed(2) + ' MB'; //M
        if (size < Math.pow(num, 4))
            return (size / Math.pow(num, 3)).toFixed(2) + ' G'; //G
        return (size / Math.pow(num, 4)).toFixed(2) + ' T'; //T
    },
    is_uuid: (uuid) => {
        let s = "" + uuid;
        s = s.match('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$');
        if (s === null) {
            return false;
        }
        return true;
    },
    relink: (uuid) => {
        if ($.is_uuid(uuid) == false) {
            uuid = $(uuid).val();
        }
        $.ajax({
            method: 'GET',
            url: '/api/relink?uuid=' + uuid,
            success: function (response) {
                $.info('请求成功')
            }
        });
    },
    join_path: (base, relative) => {
        // 移除基础目录末尾的斜杠
        base = base.replace(/\/$/, '');
        // 解析相对路径中的连续 ../
        let parts = relative.split('/');
        let stack = base.split('/');

        for (let i = 0; i < parts.length; i++) {
            if (parts[i] == '.') {
                // 跳过 ./ 目录
            } else if (parts[i] == '..') {
                if (stack.length > 1 || stack[0] != '') {
                    stack.pop();
                }
            } else {
                stack.push(parts[i]);
            }
        }
        if (stack.length == 0 || stack[0] == '') {
            if (base[0] == '.') stack[0] = './';
            else stack[0] = '/';
        }
        let path = stack.join('/');
        if (path == '.') path = './';
        return path
    },
    download_file: (url, fileName) => {
        $.ajax({
            url: url,
            method: 'GET',
            xhrFields: {
                responseType: 'blob'
            },
            success: function (data) {
                let blob = data;
                let a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = fileName;
                a.click();
            }
        });
    },
    safecode: (length = 4) => {
        let ascii_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ";
        let digits = "0123456789";
        let res = "";
        for (let i = 0; i < length; i++) {
            let choice = ascii_letters + digits;
            res += choice.charAt(Math.floor(Math.random() * choice.length));
        }
        return res;
    },
    sesdata: (data) => {
        if (typeof data === 'object' && data !== null) { // 设置数据并且返回key值
            let key = $.safecode();
            sessionStorage.setItem(key, JSON.stringify(data));
            return key;
        } else if (typeof data === 'string') { // 用key值读取数据并且删除sessionStorage
            var data_str = sessionStorage.getItem(data);
            // 如果没有这个key，返回{}
            if (data_str === null) return {};
            sessionStorage.removeItem(data);
            try {
                // 尝试解析数据
                var data = JSON.parse(data_str);
                return data;
            } catch (e) { return {} };
        } else {
            throw 'value is not object or string';
        }
    },
    diff_page: (url, data = {}, open_new = true) => {
        if (url) {
            let key = $.sesdata(data);
            if (open_new) {
                window.open(url + '?code=' + key, '_blank');
            } else {
                window.location.href = url + '?code=' + key;
            }
        } else {
            let url_params = new URLSearchParams(window.location.search);
            let code = url_params.get('code');
            let data = $.sesdata(code);
            return data;
        }
    },
    load_script: (url, callback) => {
        $.info(url)
        var script = document.createElement('script');
        script.src = url;
        script.onload = callback;
        document.head.appendChild(script);
    },
    html_escape: (str) => {
        var escape_chars = {
            '<': '<',
            '>': '>',
            '&': '&',
            '"': '"',
            "'": "'",
        };
        return str.replace(/[<>&"']/g, function (m) {
            return escape_chars[m];
        });
    },
    change_font: (element_id, font) => {
        var element = document.getElementById(element_id);
        if (element) {
            element.style.fontFamily = font;
        }
    }


});