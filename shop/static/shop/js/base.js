window.addLoadEvent = call => {
    let old_onload = window.onload;

    if (typeof window.onload !== 'function') {
        window.onload = call;
    } else {
        window.onload = function() {
            old_onload();
            call();
        }
    }
};

function form_dataset(form) {
    let dataset = [];
    let inputs = form.querySelectorAll('input');

    dataset.push('_ext_method=' + form.getAttribute('_ext_method'));
    for (let i = 0; i < inputs.length; i++) {
        dataset.push(inputs[i].name + '=' + inputs[i].value)
    }

    return dataset.join('&');
}

function default_restful_handel(form, xlr) {
    if (xlr.readyState !== 4) return;

    let data = JSON.parse(xlr.responseText);
    if (data.status === 200) {
        form.tips(data.results, 'success');
    } else {
        form.tips(data.errors, 'error');
    }
}

function form_restful_init() {
    let forms = document.querySelectorAll('form');
    for (let i = 0; i < forms.length; i++) {
        if (forms[i].getAttribute('submit-type') !== 'restful') continue;

        // 绑定表单提示
        forms[i].tips = function (value, lever) {
            let tips = this.querySelector('.tips');
            tips.classList.remove('error', 'success');

            if (value === null) {
                tips.innerText = null;
            } else {
                tips.innerText = value;
                tips.classList.add(lever);
            }
        };

        // 重定向表单提交事件
        forms[i].onsubmit = function(ev) {
            ev.preventDefault();
            let form = ev.target;
            form.tips(null, null);

            // 执行表单提交前的准备过程
            let submit_before = form.submitBefore && form.submitBefore();
            if (typeof(submit_before) === 'object' && submit_before.checked === false) {
                form.tips(submit_before.error_info, 'error');
                return
            }

            // 使用Ajax方式发送restful请求
            let xlr = new XMLHttpRequest();
            xlr.open(form.method, form.action, true);
            xlr.setRequestHeader('Accept', 'application/json');
            xlr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
            xlr.onreadystatechange = () => default_restful_handel(form, xlr);
            xlr.send(form_dataset(form));
        }
    }
}

window.addLoadEvent(function() {
    form_restful_init();
});
