const $ = mdui.$;

const Base64 = {
    // private property
    _keyStr: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="
    // public method for encoding
    , encode: function (input) {
        let output = "";
        let chr1, chr2, chr3, enc1, enc2, enc3, enc4;
        let i = 0;
        input = Base64._utf8_encode(input);
        while (i < input.length) {
            chr1 = input.charCodeAt(i++);
            chr2 = input.charCodeAt(i++);
            chr3 = input.charCodeAt(i++);
            enc1 = chr1 >> 2;
            enc2 = ((chr1 & 3) << 4) | (chr2 >> 4);
            enc3 = ((chr2 & 15) << 2) | (chr3 >> 6);
            enc4 = chr3 & 63;
            if (isNaN(chr2)) {
                enc3 = enc4 = 64;
            }
            else if (isNaN(chr3)) {
                enc4 = 64;
            }
            output = output +
                this._keyStr.charAt(enc1) + this._keyStr.charAt(enc2) +
                this._keyStr.charAt(enc3) + this._keyStr.charAt(enc4);
        } // Whend 
        return output;
    } // End Function encode 
    // public method for decoding
    , decode: function (input) {
        let output = "";
        let chr1, chr2, chr3;
        let enc1, enc2, enc3, enc4;
        let i = 0;
        input = input.replace(/[^A-Za-z0-9\+\/\=]/g, "");
        while (i < input.length) {
            enc1 = this._keyStr.indexOf(input.charAt(i++));
            enc2 = this._keyStr.indexOf(input.charAt(i++));
            enc3 = this._keyStr.indexOf(input.charAt(i++));
            enc4 = this._keyStr.indexOf(input.charAt(i++));
            chr1 = (enc1 << 2) | (enc2 >> 4);
            chr2 = ((enc2 & 15) << 4) | (enc3 >> 2);
            chr3 = ((enc3 & 3) << 6) | enc4;
            output = output + String.fromCharCode(chr1);
            if (enc3 != 64) {
                output = output + String.fromCharCode(chr2);
            }

            if (enc4 != 64) {
                output = output + String.fromCharCode(chr3);
            }

        } // Whend 
        output = Base64._utf8_decode(output);
        return output;
    } // End Function decode 

    // private method for UTF-8 encoding
    , _utf8_encode: function (string) {
        let utftext = "";
        string = string.replace(/\r\n/g, "\n");

        for (let n = 0; n < string.length; n++) {
            let c = string.charCodeAt(n);

            if (c < 128) {
                utftext += String.fromCharCode(c);
            }
            else if ((c > 127) && (c < 2048)) {
                utftext += String.fromCharCode((c >> 6) | 192);
                utftext += String.fromCharCode((c & 63) | 128);
            }
            else {
                utftext += String.fromCharCode((c >> 12) | 224);
                utftext += String.fromCharCode(((c >> 6) & 63) | 128);
                utftext += String.fromCharCode((c & 63) | 128);
            }
        } // Next n 
        return utftext;
    } // End Function _utf8_encode 
    // private method for UTF-8 decoding
    , _utf8_decode: function (utftext) {
        let string = "";
        let i = 0;
        let c, c1, c2, c3;
        c = c1 = c2 = 0;

        while (i < utftext.length) {
            c = utftext.charCodeAt(i);

            if (c < 128) {
                string += String.fromCharCode(c);
                i++;
            }
            else if ((c > 191) && (c < 224)) {
                c2 = utftext.charCodeAt(i + 1);
                string += String.fromCharCode(((c & 31) << 6) | (c2 & 63));
                i += 2;
            }
            else {
                c2 = utftext.charCodeAt(i + 1);
                c3 = utftext.charCodeAt(i + 2);
                string += String.fromCharCode(((c & 15) << 12) | ((c2 & 63) << 6) | (c3 & 63));
                i += 3;
            }
        } // Whend 
        return string;
    } // End Function _utf8_decode 

}

$.extend({
    info: (info) => {
        mdui.snackbar({
            message: info,
            closeOnOutsideClick: true
        })
    },
    online_clients: (func_suc, func_err) => {
        $.ajax({
            method: 'GET',
            url: '/api/online_clients',
            success: function (response) {
                if (response)
                    try {
                        online_clients = response;
                        if (func_suc != null) func_suc()
                        console.log('Get online_clients successful')
                    } catch (err) {
                        online_clients = {};
                        console.log('Unable to get online_clients')
                        if (func_err != null) func_err()
                    }
            }
        })
    },
    reload_select: (id) => {
        $.online_clients(
            () => {
                let select_html = '';
                for (let client_uuid in online_clients) {
                    let client_html = selects.replace('UUID', client_uuid).replace('NAME', client_uuid)
                    select_html += client_html
                }
                $(id).html(select_html)
                $.info('刷新完成')
            }, () => {
                $.info('无法获取数据')
            }
        )
    },
    is_online: (uuid) => {
        if (uuid == '') {
            $.info('未选择设备')
            return false
        }
        if (!(uuid in online_clients)) {
            $.info('设备离线')
            return false
        }
        return true
    },
    bytes_resize: (size) => {
        if (!size) return '';
        let num = 1024.00 //byte
        if (size < num)
            return size + ' B'
        if (size < Math.pow(num, 2))
            return (size / num).toFixed(2) + ' KB' //kb
        if (size < Math.pow(num, 3))
            return (size / Math.pow(num, 2)).toFixed(2) + ' MB' //M
        if (size < Math.pow(num, 4))
            return (size / Math.pow(num, 3)).toFixed(2) + ' G' //G
        return (size / Math.pow(num, 4)).toFixed(2) + ' T' //T
    },
    is_uuid: (uuid) => {
        let s = "" + uuid;
        s = s.match('^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$');
        if (s === null) {
            return false
        }
        return true
    },
    relink: (uuid) => {
        if ($.is_uuid(uuid) == false) {
            uuid = $(uuid).val()
        }
        $.ajax({
            method: 'GET',
            url: '/api/relink?uuid=' + uuid,
            success: function (response) {
                $.info('请求成功')
            }
        })
    },
    join_path: (base, relative) => {
        // 移除基础目录末尾的斜杠
        base = base.replace(/\/$/, '')
        // 解析相对路径中的连续 ../
        let parts = relative.split('/')
        let stack = base.split('/')

        for (let i = 0; i < parts.length; i++) {
            if (parts[i] == '.') {
                // 跳过 ./ 目录
            } else if (parts[i] == '..') {
                if (stack.length > 1 || stack[0] != '') {
                    stack.pop()
                }
            } else {
                stack.push(parts[i])
            }
        }
        if (stack.length == 0 || stack[0] == '') {
            if (base[0] == '.') stack[0] = './'
            else stack[0] = '/'
        }
        let path = stack.join('/')
        if (path == '.') path = './'
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
                let blob = data
                let a = document.createElement('a')
                a.href = URL.createObjectURL(blob)
                a.download = fileName
                a.click()
            }
        })
    },
    safecode: (length = 4) => {
        let ascii_letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        let digits = "0123456789"
        let res = ""
        for (let i = 0; i < length; i++) {
            let choice = ascii_letters + digits
            res += choice.charAt(Math.floor(Math.random() * choice.length))
        }
        return res
    },
    sesdata: (data) => {
        if (typeof data === 'object' && data !== null) { // 设置数据并且返回key值
            let key = $.safecode()
            sessionStorage.setItem(key, JSON.stringify(data))
            return key
        } else if (typeof data === 'string') { // 用key值读取数据并且删除sessionStorage
            var data_str = sessionStorage.getItem(data)
            // 如果没有这个key，返回{}
            if (data_str === null) return {}
            sessionStorage.removeItem(data)
            try {
                // 尝试解析数据
                var data = JSON.parse(data_str)
                return data;
            } catch (e) { return {} }
        } else {
            return {}
        }
    },
    diff_page: (url, data = {}, open_new = true) => {
        if (url) {
            let key = $.sesdata(data)
            if (open_new) {
                window.open(url + '?code=' + key, '_blank')
            } else {
                window.location.href = url + '?code=' + key
            }
        } else {
            let url_params = new URLSearchParams(window.location.search)
            let code = url_params.get('code')
            let data = $.sesdata(code)
            return data
        }
    },
    load_script: (url, callback) => {
        $.info(url)
        var script = document.createElement('script')
        script.src = url
        script.onload = callback
        document.head.appendChild(script)
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
            return escape_chars[m]
        })
    },
    change_font: (element_id, font) => {
        var element = document.getElementById(element_id)
        if (element) {
            element.style.fontFamily = font
        }
    },
    base64_encode: (text) => {
        return Base64.encode(text)
    },
    base64_decode: (text) => {
        return Base64.decode(text)
    },
    title: (title) => {
        document.title = title
    }

});